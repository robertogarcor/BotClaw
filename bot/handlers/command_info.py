import subprocess
import logging
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.i18n import _
from bot.servers.factory import ServerFactory
from bot.services.session_manager import SessionManager
from bot.services.user_manager import UserManager

logger = logging.getLogger(__name__)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)
    
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text(_("init_first", lang=lang))
        return

    voice_mode = context.user_data.get("voice_mode", user.voice_mode if user else "off")
    voice_emoji = "🎤" if voice_mode == "on" else "🔇"

    project_name = Path(current_path).name

    status_text = _("status_header", lang=lang)
    status_text += _("status_project", lang=lang, name=project_name)
    status_text += _("status_path", lang=lang, path=current_path)

    session = session_manager.get_session(chat_id, current_path)
    if session and session.session_id:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )
        
        status_text += _("status_session", lang=lang, sid=session.session_id)
        
        try:
            session_details = server.get_session_details(session.session_id)
            if session_details:
                title = session_details.get("title", "")
                if title:
                    title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
                    status_text += _("status_title", lang=lang, title=title_escaped)
        except Exception:
            pass
        
        if session.created_at:
            try:
                if isinstance(session.created_at, str):
                    dt = datetime.fromisoformat(session.created_at.replace('Z', '+00:00'))
                else:
                    dt = session.created_at
                created_str = dt.strftime("%d-%m-%Y %H:%M")
            except:
                created_str = str(session.created_at)
            status_text += _("status_created", lang=lang, date=created_str)
        
        if session.last_access:
            try:
                if isinstance(session.last_access, str):
                    dt = datetime.fromisoformat(session.last_access.replace('Z', '+00:00'))
                else:
                    dt = session.last_access
                last_access_str = dt.strftime("%d-%m-%Y %H:%M")
            except:
                last_access_str = str(session.last_access)
            status_text += _("status_last_access", lang=lang, date=last_access_str)

        try:
            session_details = server.get_session_details(session.session_id)
            if session_details:
                model_data = session_details.get("model")
                if not isinstance(model_data, dict):
                    model_data = session_details.get("info", {}).get("model", {})

                model_id = "unknown"
                provider_id = "unknown"
                if isinstance(model_data, dict):
                    model_id = (
                        model_data.get("id")
                        or model_data.get("modelID")
                        or model_data.get("modelId")
                        or "unknown"
                    )
                    provider_id = (
                        model_data.get("providerID")
                        or model_data.get("providerId")
                        or model_data.get("provider")
                        or "unknown"
                    )
                elif isinstance(model_data, str) and model_data.strip():
                    model_id = model_data.strip()

                agent = (
                    session_details.get("agent")
                    or session_details.get("agentName")
                    or session_details.get("info", {}).get("agent")
                    or "unknown"
                )

                mode = (
                    session_details.get("mode")
                    or session_details.get("info", {}).get("mode")
                    or "N/A"
                )

                agents = server.list_agents()
                if agent != "unknown" and agents:
                    for a in agents:
                        if not isinstance(a, dict):
                            continue
                        name = a.get("name") or a.get("id")
                        if name == agent:
                            mode = a.get("mode") or mode
                            break

                if model_id == "unknown" or provider_id == "unknown" or agent == "unknown":
                    messages = server.get_session_messages(session.session_id)
                    for msg in reversed(messages):
                        if not isinstance(msg, dict):
                            continue
                        info = msg.get("info", {})
                        if not isinstance(info, dict):
                            continue

                        nested_model = info.get("model", {}) if isinstance(info.get("model"), dict) else {}

                        if model_id == "unknown":
                            model_id = (
                                info.get("modelID")
                                or info.get("modelId")
                                or nested_model.get("modelID")
                                or nested_model.get("id")
                                or model_id
                            )

                        if provider_id == "unknown":
                            provider_id = (
                                info.get("providerID")
                                or info.get("providerId")
                                or nested_model.get("providerID")
                                or nested_model.get("provider")
                                or provider_id
                            )

                        if agent == "unknown":
                            agent = info.get("agent") or info.get("agentName") or agent

                        if mode == "N/A":
                            mode = info.get("mode") or mode

                        if model_id != "unknown" and provider_id != "unknown" and agent != "unknown":
                            break

                selected_mode = context.user_data.get("agent_mode")
                selected_mode_str = selected_mode if selected_mode in ("build", "plan") else "(not set)"

                model_display = model_id
                provider_display = provider_id
                agent_display = agent
                mode_effective_display = mode

                if model_id == "unknown" and provider_id == "unknown":
                    model_display = "pending first response"
                    provider_display = "pending"

                if agent == "unknown":
                    agent_display = "pending first response"

                if mode == "N/A":
                    mode_effective_display = "pending"

                status_text += _("status_model", lang=lang, model=model_display, provider=provider_display)
                status_text += _("status_agent", lang=lang, agent=agent_display)
                status_text += _("status_mode", lang=lang, selected=selected_mode_str, effective=mode_effective_display)
            else:
                status_text += _("status_model_na", lang=lang)
                status_text += _("status_agent_na", lang=lang)
                status_text += _("status_mode_na", lang=lang)
        except Exception as e:
            status_text += _("status_model_error", lang=lang)
            status_text += _("status_agent_error", lang=lang)
            status_text += _("status_mode_error", lang=lang)
    else:
        status_text += _("status_session_none", lang=lang)

    if Path(current_path).exists():
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=current_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                status_text += _("status_git_ok", lang=lang)
            else:
                status_text += _("status_git_fail", lang=lang)
        except FileNotFoundError:
            status_text += _("status_git_not_installed", lang=lang)
    else:
        status_text += _("status_git_fail", lang=lang)

    status_text += _("status_voice", lang=lang, emoji=voice_emoji, mode=voice_mode.upper())

    await update.message.reply_text(status_text, parse_mode="Markdown")


async def mcp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = context.user_data.get("lang", "en")
    try:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        mcp_servers = server.list_mcp_servers()

        if not mcp_servers:
            await update.message.reply_text(_("mcp_none", lang=lang))
            return

        response_text = _("mcp_header", lang=lang)
        for name, status in mcp_servers.items():
            status_text = status.get("status", "")
            status_emoji = "✅" if "connected" in status_text.lower() else "❌"
            response_text += _("mcp_item", lang=lang, emoji=status_emoji, name=name, status=status_text) + "\n"

        await update.message.reply_text(response_text[:4096], parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text(_("init_first", lang=lang))
        return

    skills_dir = Path(current_path) / ".agents" / "skills"

    if not skills_dir.exists():
        await update.message.reply_text(_("skills_no_dir", lang=lang))
        return

    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                try:
                    content = skill_md.read_text()
                    name = item.name
                    description = ""
                    for line in content.split("\n"):
                        if line.startswith("description:"):
                            description = line.replace("description:", "").strip()
                            break
                    skills.append({"name": name, "description": description})
                except Exception:
                    pass

    if not skills:
        await update.message.reply_text(_("skills_none", lang=lang))
        return

    response_text = _("skills_header", lang=lang)
    for skill in skills:
        response_text += _("skills_item", lang=lang, name=skill['name'], desc=skill['description'] or "")
        response_text += "\n\n"

    await update.message.reply_text(response_text[:4096], parse_mode="Markdown")


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text(_("init_first", lang=lang))
        return

    session = session_manager.get_session(chat_id, current_path)
    if not session or not session.session_id:
        await update.message.reply_text(_("no_active_session", lang=lang))
        return

    current_mode = context.user_data.get("agent_mode")

    if not current_mode:
        try:
            server = ServerFactory.create_opencode(
                url=Settings.OPENCODE_SERVER_URL,
                password=Settings.OPENCODE_SERVER_PASSWORD
            )
            messages = server.get_session_messages(session.session_id)
            for msg in reversed(messages):
                if not isinstance(msg, dict):
                    continue
                info = msg.get("info", {})
                if not isinstance(info, dict):
                    continue
                mode = info.get("mode")
                if mode in ("build", "plan"):
                    current_mode = mode
                    break
        except Exception:
            current_mode = None

    if current_mode not in ("build", "plan"):
        current_mode = "build"

    new_mode = "plan" if current_mode == "build" else "build"
    context.user_data["agent_mode"] = new_mode

    await update.message.reply_text(_("mode_changed", lang=lang, mode=new_mode), parse_mode="Markdown")
