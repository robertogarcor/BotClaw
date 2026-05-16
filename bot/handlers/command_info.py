import subprocess
import logging
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.servers.factory import ServerFactory

logger = logging.getLogger(__name__)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager
    from bot.services.user_manager import UserManager

    chat_id = update.effective_chat.id
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)
    
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text("Use /init first to set up your project.")
        return

    voice_mode = context.user_data.get("voice_mode", user.voice_mode if user else "off")
    voice_emoji = "🎤" if voice_mode == "on" else "🔇"

    project_name = Path(current_path).name

    status_text = f"📁 *Status*\n\n"
    status_text += f"Project: `{project_name}`\n"
    status_text += f"Dir: `{current_path}`\n"

    session = session_manager.get_session(chat_id, current_path)
    if session and session.session_id:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )
        
        status_text += f"Session: `{session.session_id}`\n"
        
        try:
            session_details = server.get_session_details(session.session_id)
            if session_details:
                title = session_details.get("title", "")
                if title:
                    title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
                    status_text += f"Title: {title_escaped}\n"
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
            status_text += f"Created: {created_str}\n"
        
        if session.last_access:
            try:
                if isinstance(session.last_access, str):
                    dt = datetime.fromisoformat(session.last_access.replace('Z', '+00:00'))
                else:
                    dt = session.last_access
                last_access_str = dt.strftime("%d-%m-%Y %H:%M")
            except:
                last_access_str = str(session.last_access)
            status_text += f"Last access: {last_access_str}\n"

        try:
            session_details = server.get_session_details(session.session_id)
            if session_details:
                model_data = session_details.get("model", {})
                model_id = model_data.get("id", "unknown")
                provider_id = model_data.get("providerID", "unknown")
                agent = session_details.get("agent", "unknown")
                mode = session_details.get("mode", "N/A")
                status_text += f"Model: {model_id} ({provider_id})\n"
                status_text += f"Agent: {agent} | Mode: {mode}\n"
            else:
                status_text += "Model: (info not available)\n"
                status_text += "Agent: (info not available) | Mode: (info not available)\n"
        except Exception as e:
            status_text += "Model: (error getting info)\n"
            status_text += "Agent: (error) | Mode: (error)\n"
    else:
        status_text += "Session: ❌ None\n"

    if Path(current_path).exists():
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=current_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                status_text += f"Git: ✅\n"
            else:
                status_text += f"Git: ❌\n"
        except FileNotFoundError:
            status_text += f"Git: ❌ (not installed)\n"
    else:
        status_text += f"Git: ❌\n"

    status_text += f"Voice: {voice_emoji} {voice_mode.upper()}"

    await update.message.reply_text(status_text, parse_mode="Markdown")


async def mcp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        mcp_servers = server.list_mcp_servers()

        if not mcp_servers:
            await update.message.reply_text("🔌 *MCP Servers:*\n\nNo MCP servers connected.")
            return

        response_text = "🔌 *MCP Servers:*\n\n"
        for name, status in mcp_servers.items():
            status_emoji = "✅" if status.get("connected") else "❌"
            response_text += f"{status_emoji} *{name}*\n"
            if status.get("status"):
                response_text += f"   Status: {status.get('status')}\n"

        await update.message.reply_text(response_text[:4096], parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text("Use /init to set your project first.")
        return

    skills_dir = Path(current_path) / ".agents" / "skills"

    if not skills_dir.exists():
        await update.message.reply_text("🛠️ *Skills:*\n\nNo skills directory found for this project.")
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
        await update.message.reply_text("🛠️ *Skills:*\n\nNo skills found for this project.")
        return

    response_text = "🛠️ *Skills*\n\n"
    for skill in skills:
        response_text += f"• *{skill['name']}*\n"
        if skill['description']:
            response_text += f"  {skill['description']}\n"
        response_text += "\n"

    await update.message.reply_text(response_text[:4096], parse_mode="Markdown")
