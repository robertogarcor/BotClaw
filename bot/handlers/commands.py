import subprocess
import logging
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.servers.factory import ServerFactory

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if (Settings.USERS_ALLOWED or Settings.USER_IDS_ALLOWED) and not Settings.is_user_allowed(user.username, user.id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    welcome_text = (
        "Welcome to BotClaw! 🚀\n\n"
        "I'm your gateway to OpenCode from Telegram.\n\n"
        "Use /help to see available commands.\n"
        "Use /init to set your working directory."
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 *BotClaw Commands*\n\n"
        
        "🚀 *Getting Started*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/status - Show current status\n"
        "/project - Show current project\n\n"
        
        "📁 *Project*\n"
        "/init <path> - Set working directory\n"
        "/project - Show current project info\n"
        "/projects - List all your projects\n"
        "/clone <url> - Clone git repository\n\n"
        
        "💬 *Sessions*\n"
        "/new - Start new session\n"
        "/sessions - List sessions of current project\n"
        "/sessions <path> - List sessions of a specific project\n"
        "/use <id> - Select a session\n"
        "/last - Use last session\n\n"
        
        "🎤 *Voice*\n"
        "/voice - Toggle voice mode\n"
        "/voice on - All replies as voice\n"
        "/voice off - Text replies only\n"
        "/voice status - Show voice mode\n\n"
        
        "🔧 *Utilities*\n"
        "/mcp - Show MCP servers\n"
        "/skills - Show project skills\n"
        "/cancel - Cancel current operation\n\n"
        
        "_Just send me a message or voice to chat with OpenCode!_"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager
    from bot.services.user_manager import UserManager
    from bot.servers.factory import ServerFactory
    from bot.config.settings import Settings
    import subprocess

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
            from datetime import datetime
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
            from datetime import datetime
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


async def project_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.user_manager import UserManager
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text("📁 *Project:*\n\nNo project set.\nUse `/init <path>` to set your project.")
        return

    project_name = Path(current_path).name
    session = session_manager.get_session(chat_id, current_path)
    current_session_id = session.session_id if session and session.session_id else "None"

    skills_dir = Path(current_path) / ".agents" / "skills"
    skills = []
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir():
                skills.append(item.name)

    response = f"📁 *Project:*\n\n"
    response += f"Name: `{project_name}`\n"
    response += f"Path: `{current_path}`\n"
    response += f"Session: `{current_session_id}`\n"
    if skills:
        response += f"Skills: {', '.join(skills)}"

    await update.message.reply_text(response, parse_mode="Markdown")


async def projects_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager
    from bot.servers.factory import ServerFactory

    chat_id = update.effective_chat.id
    session_manager = SessionManager()

    try:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        projects = server._session.get(
            f"{server.url}/project",
            timeout=30
        )

        if projects.status_code != 200:
            await update.message.reply_text("📂 *Projects:*\n\nFailed to fetch projects from API.")
            return

        projects_data = projects.json()
        projects_data = [p for p in projects_data if p.get("id") != "global"]

        if not projects_data:
            await update.message.reply_text("📂 *Projects:*\n\nNo projects found.\nUse `/init <path>` to start.")
            return

        response = "📂 *Projects:*\n\n"
        for project in projects_data:
            project_path = project.get("worktree", "")
            time_data = project.get("time", {})
            created_ts = time_data.get("created", 0)
            updated_ts = time_data.get("updated", 0)

            if created_ts:
                created_str = datetime.fromtimestamp(created_ts / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                created_str = "unknown"

            if updated_ts:
                last_access_str = datetime.fromtimestamp(updated_ts / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                last_access_str = "unknown"

            sessions = session_manager.get_sessions_from_api(project_path)
            session_id = sessions[0].get("id", "None") if sessions else "None"

            if not project_path and sessions:
                project_path = sessions[0].get("directory", "")

            project_name = Path(project_path).name if project_path else "unknown"

            response += f"• *{project_name}*\n"
            response += f"  Path: `{project_path}`\n"
            response += f"  Session: `{session_id}`\n"
            response += f"  Created: {created_str}\n"
            response += f"  Last access: {last_access_str}\n\n"

        await update.message.reply_text(response[:4096], parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def init_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.user_manager import UserManager
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text("Usage: /init <path>\nExample: /init /home/user/myproject")
        return

    path = " ".join(args)
    full_path = str(Path(path).expanduser().resolve())

    if not Path(full_path).exists():
        await update.message.reply_text(f"❌ Path does not exist: {full_path}")
        return

    session_manager = SessionManager()
    user_manager = UserManager()

    try:
        user_manager.get_or_create_user(chat_id, update.effective_user.username or str(chat_id))

        logger.info(f"Initializing project: {full_path}")
        session_id, is_new, session_data = session_manager.init_project(chat_id, full_path)
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error initializing project: {str(e)}")
        return
    
    title = session_data.get("title", "") if session_data else ""
    time_data = session_data.get("time", {}) if session_data else {}
    created_ts = time_data.get("created", 0)
    updated_ts = time_data.get("updated", 0)
    
    from datetime import datetime
    created_str = datetime.fromtimestamp(created_ts / 1000).strftime("%d-%m-%Y %H:%M") if created_ts else None
    updated_str = datetime.fromtimestamp(updated_ts / 1000).strftime("%d-%m-%Y %H:%M") if updated_ts else None

    logger.info("Checking for AGENTS.md and SPEC.md...")
    agents_path = Path(full_path) / "AGENTS.md"
    spec_path = Path(full_path) / "SPEC.md"

    context_loaded = []
    context_text = ""

    if agents_path.exists():
        try:
            agents_content = agents_path.read_text()
            context_text += f"--- AGENTS.md ---\n{agents_content}\n"
            context_loaded.append("AGENTS.md")
        except Exception:
            pass

    if spec_path.exists():
        try:
            spec_content = spec_path.read_text()
            context_text += f"\n--- SPEC.md ---\n{spec_content}\n"
            context_loaded.append("SPEC.md")
        except Exception:
            pass

    session = session_manager.get_session(chat_id, full_path)
    if session and session.session_id and context_text:
        await update.message.reply_text("⏳ Loading project context...")
        try:
            server = session_manager.get_server()
            project_name = Path(full_path).name
            prompt = (
                f"IMPORTANTE: Proyecto actual = {project_name}\n"
                f"Directorio de trabajo: {full_path}\n\n"
                f"Contexto del proyecto:\n{context_text}\n\n"
                f"Este es el único proyecto activo. Olvida cualquier proyecto anterior."
            )
            response = server.send_prompt(session.session_id, prompt)
            logger.info(f"Context loaded, response received")
        except Exception as e:
            logger.error(f"Failed to load context: {e}")

    if context_loaded:
        project_name = Path(full_path).name
        if is_new:
            msg = (
                f"✅ *{project_name}* configurado\n\n"
                f"Dir: `{full_path}`\n"
                f"Session: `{session_id}`\n"
                f"📄 Context: {', '.join(context_loaded)}\n\n"
                f"*Listo para recibir mensajes.*"
            )
        else:
            msg = (
                f"✅ *{project_name}* configurado\n\n"
                f"Dir: `{full_path}`\n"
                f"Session: `{session_id}`\n"
            )
            if title:
                title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
                msg += f"Title: {title_escaped}\n"
            if created_str:
                msg += f"Created: {created_str}\n"
            if updated_str:
                msg += f"Last access: {updated_str}\n"
            msg += f"📄 Context: {', '.join(context_loaded)}\n\n"
            msg += f"*Listo para recibir mensajes.*"
        try:
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending /init message: {type(e).__name__}: {e}")
    else:
        project_name = Path(full_path).name
        if is_new:
            msg = (
                f"✅ *{project_name}* configurado\n\n"
                f"Dir: `{full_path}`\n"
                f"Session: `{session_id}`\n\n"
                f"*Listo para recibir mensajes.*"
            )
        else:
            msg = (
                f"✅ *{project_name}* configurado\n\n"
                f"Dir: `{full_path}`\n"
                f"Session: `{session_id}`\n"
            )
            if title:
                title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
                msg += f"Title: {title_escaped}\n"
            if created_str:
                msg += f"Created: {created_str}\n"
            if updated_str:
                msg += f"Last access: {updated_str}\n"
            msg += f"\n*Listo para recibir mensajes.*"
        try:
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending /init message: {type(e).__name__}: {e}")


async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text("Usage: /clone <repo_url>\nExample: /clone https://github.com/user/repo.git")
        return

    repo_url = args[0]
    session_manager = SessionManager()

    current_path = session_manager.get_current_path(chat_id)
    base_dir = str(Path(current_path).parent) if current_path else str(Path.home() / "projects")
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    target_dir = Path(base_dir) / repo_name

    if target_dir.exists():
        await update.message.reply_text(f"📁 Directory already exists: {target_dir}\nUse /init {target_dir} to use it.")
        return

    await update.message.reply_text(f"🔄 Cloning {repo_url}...")

    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            check=True,
            capture_output=True
        )

        await update.message.reply_text(f"✅ Cloned to:\n`{target_dir}`\n\nUse /init {target_dir} to start working with it.", parse_mode="Markdown")

    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ Git error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
    except FileNotFoundError:
        await update.message.reply_text("❌ Git is not installed on this server.")


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()

    try:
        working_dir = session_manager.get_current_path(chat_id)
        if not working_dir:
            await update.message.reply_text("Set your project first with /init <path>")
            return

        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        session_manager.set_server(server)
        new_session_id = session_manager.create_session_with_dir(chat_id, working_dir)

        if new_session_id:
            await update.message.reply_text(f"✅ New session created for:\n`{working_dir}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Failed to create new session")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Operation cancelled.")


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    session_manager = SessionManager()

    if args:
        path = " ".join(args)
        full_path = str(Path(path).expanduser().resolve())
    else:
        full_path = session_manager.get_current_path(chat_id)
        if not full_path:
            await update.message.reply_text("No project set. Use /init <path> first or specify a path: /sessions <path>")
            return

    logger.info(f"Listing sessions for: {full_path}")

    try:
        sessions = session_manager.get_sessions_from_api(full_path)

        session_manager.sync_session_dates_from_api(chat_id, full_path)

        if not sessions:
            await update.message.reply_text(
                f"No sessions found for:\n{full_path}\n\n"
                "Use /init to initialize the project."
            )
            return

        response_text = f"📋 *Sessions for* `{full_path}`\n\n"

        for session in sessions[:10]:
            session_id = session.get("id", "")
            title = session.get("title", "")
            time_data = session.get("time", {})
            created = time_data.get("created", 0)
            updated = time_data.get("updated", 0)
            
            from datetime import datetime
            if created:
                created_str = datetime.fromtimestamp(created / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                created_str = "unknown"
            
            if updated:
                last_access_str = datetime.fromtimestamp(updated / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                last_access_str = "unknown"

            response_text += f"• Session: `{session_id}`\n"
            title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`").replace("[", r"\[").replace("]", r"\]").replace("(", r"\(").replace(")", r"\)")
            response_text += f"  Title: {title_escaped or 'Untitled'}\n"
            response_text += f"  Created: {created_str}\n"
            response_text += f"  Last access: {last_access_str}\n"

        await update.message.reply_text(response_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


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


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text(
            "Usage: /use <session_id>\n"
            "Use /sessions to see available sessions, then copy the session ID."
        )
        return

    session_id_prefix = args[0].strip()
    logger.info(f"use_command: trying session_id={session_id_prefix}")

    try:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        session_details = server.get_session_details(session_id_prefix)

        if not session_details:
            sessions = server.list_sessions()
            for session in sessions:
                if session.get("id", "").startswith(session_id_prefix):
                    session_id = session.get("id", "")
                    session_details = server.get_session_details(session_id)
                    logger.info(f"use_command: found by prefix: {session_id}")
                    break

        if not session_details:
            await update.message.reply_text("❌ Session not found.")
            return

        session_id = session_details.get("id", session_id_prefix)
        directory = session_details.get("directory", "")
        session_manager = SessionManager()
        if directory:
            session_manager.set_session_id(chat_id, directory, session_id)

        title = session_details.get("title", "Unknown")
        title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
        await update.message.reply_text(f"✅ Now using session:\nTitle: {title_escaped}\nDir: `{directory}`", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def last_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()

    try:
        saved_session = session_manager.get_current_session(chat_id)
        if saved_session and saved_session.session_id:
            server = ServerFactory.create_opencode(
                url=Settings.OPENCODE_SERVER_URL,
                password=Settings.OPENCODE_SERVER_PASSWORD
            )
            if server.continue_session(saved_session.session_id):
                session_manager.set_session_id(chat_id, saved_session.path, saved_session.session_id)
                await update.message.reply_text(
                    f"✅ Using saved session:\nID: `{saved_session.session_id}`\nDir: `{saved_session.path}`"
                )
                return

        user_dir = session_manager.get_current_path(chat_id)
        if not user_dir:
            await update.message.reply_text("Use /init to set your project directory first.")
            return

        user_dir = user_dir.rstrip("/")

        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        sessions = server.list_sessions()

        matching_sessions = []
        tui_sessions = []
        for session in sessions:
            directory = session.get("directory", "").rstrip("/")
            title = session.get("title", "")
            if directory.startswith(user_dir) or user_dir.startswith(directory):
                if title and not title.startswith("BotClaw session for"):
                    tui_sessions.append(session)
                else:
                    matching_sessions.append(session)

        if not tui_sessions and not matching_sessions:
            await update.message.reply_text(
                f"No sessions found for:\n{user_dir}\n\n"
                "Use /new to create a new session."
            )
            return

        if tui_sessions:
            latest_session = tui_sessions[0]
        else:
            latest_session = matching_sessions[0]

        session_id = latest_session.get("id", "")
        title = latest_session.get("title", "Untitled")
        title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")

        session_manager = SessionManager()
        session_manager.set_session_id(chat_id, user_dir, session_id)

        await update.message.reply_text(f"✅ Connected to latest session:\nTitle: {title_escaped}\nDir: `{user_dir}`", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        current = context.user_data.get("voice_mode", "off")
        new_mode = "off" if current == "on" else "on"
        context.user_data["voice_mode"] = new_mode
        if new_mode == "on":
            await update.message.reply_text("🎤 Voice mode: ON\nAll replies will be sent as voice.")
        else:
            await update.message.reply_text("🔇 Voice mode: OFF\nReplies will be sent as text.")
        return

    subcommand = args[0].lower()

    if subcommand == "on":
        context.user_data["voice_mode"] = "on"
        await update.message.reply_text("🎤 Voice mode: ON\nAll replies will be sent as voice.")

    elif subcommand == "off":
        context.user_data["voice_mode"] = "off"
        await update.message.reply_text("🔇 Voice mode: OFF\nReplies will be sent as text.")

    elif subcommand == "status":
        mode = context.user_data.get("voice_mode", "off")
        status_text = f"🎤 Voice Mode: *{mode}*\n\n"
        status_text += "• `on` - All replies as voice\n"
        status_text += "• `off` - Text replies only"
        await update.message.reply_text(status_text, parse_mode="Markdown")

    else:
        await update.message.reply_text(
            "Usage: /voice [on|off|status]\n"
            "  /voice - Toggle on/off\n"
            "  /voice on - All replies as voice\n"
            "  /voice off - Text replies only\n"
            "  /voice status - Show current mode"
        )