import subprocess
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.servers.factory import ServerFactory


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
        "/clone <url> - Clone git repository\n\n"
        
        "💬 *Sessions*\n"
        "/new - Start new session\n"
        "/sessions - List TUI sessions\n"
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
    from bot.services.user_manager import UserManager
    from bot.services.session_manager import SessionManager
    from bot.servers.factory import ServerFactory
    from bot.config.settings import Settings
    import subprocess

    chat_id = update.effective_chat.id
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)

    if not user:
        await update.message.reply_text("Use /init first to set up your project.")
        return

    voice_mode = context.user_data.get("voice_mode", "off")
    voice_emoji = "🎤" if voice_mode == "on" else "🔇"

    project_name = Path(user.working_dir).name if user.working_dir else "Not set"

    status_text = f"📁 *Status*\n\n"
    status_text += f"Project: `{project_name}`\n"
    status_text += f"Dir: `{user.working_dir or 'Not set'}`\n"

    session_manager = SessionManager()
    session = session_manager.get_session(chat_id)
    if session and session.session_id:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )
        
        status_text += f"Session: `{session.session_id}`\n"

        try:
            response = server.send_prompt(session.session_id, ".")
            if hasattr(response, 'info') and response.info:
                model_id = response.info.get("modelID", "unknown")
                provider_id = response.info.get("providerID", "unknown")
                agent = response.info.get("agent", "unknown")
                mode = response.info.get("mode", "unknown")
                status_text += f"Model: `{model_id}` ({provider_id})\n"
                status_text += f"Agent: `{agent}` | Mode: `{mode}`\n"
            else:
                status_text += "Model: (info not available)\n"
                status_text += "Agent: (info not available) | Mode: (info not available)\n"
        except Exception as e:
            status_text += "Model: (error getting info)\n"
            status_text += "Agent: (error) | Mode: (error)\n"
    else:
        status_text += "Session: ❌ None\n"

    if user.working_dir and Path(user.working_dir).exists():
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=user.working_dir,
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
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)

    if not user or not user.working_dir:
        await update.message.reply_text("📁 *Project:*\n\nNo project set.\nUse `/init <path>` to set your project.")
        return

    project_name = Path(user.working_dir).name

    session_manager = SessionManager()
    session = session_manager.get_session(chat_id)
    current_session_id = session.session_id if session.session_id else "None"

    skills_dir = Path(user.working_dir) / ".agents" / "skills"
    skills = []
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir():
                skills.append(item.name)

    response = f"📁 *Project:*\n\n"
    response += f"Name: `{project_name}`\n"
    response += f"Path: `{user.working_dir}`\n"
    response += f"Session: `{current_session_id}`\n"
    if skills:
        response += f"Skills: {', '.join(skills)}"

    await update.message.reply_text(response, parse_mode="Markdown")


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

    user_manager = UserManager()
    user_manager.set_working_dir(chat_id, full_path)

    session_manager = SessionManager()
    session_id = session_manager.set_working_dir(chat_id, full_path)

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

    if session_id and context_text:
        await update.message.reply_text("⏳ Loading project context...")
        try:
            server = session_manager.get_server()
            project_name = Path(full_path).name
            prompt = (
                f"Eres el agente de este proyecto: {project_name}\n\n"
                f"Contexto del proyecto:\n{context_text}\n\n"
                f"Directorio de trabajo: {full_path}\n"
                f"Este es tu proyecto activo. Usa este contexto para responder preguntas."
            )
            server.send_prompt(session_id, prompt)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to load context: {e}")

    if context_loaded:
        await update.message.reply_text(
            f"✅ Working directory set to:\n`{full_path}`\n\n"
            f"📄 Context loaded: {', '.join(context_loaded)}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"✅ Working directory set to:\n`{full_path}`",
            parse_mode="Markdown"
        )


async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.user_manager import UserManager
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text("Usage: /clone <repo_url>\nExample: /clone https://github.com/user/repo.git")
        return

    repo_url = args[0]
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)

    base_dir = user.working_dir if user and user.working_dir else str(Path.home() / "projects")
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

        user_manager.set_working_dir(chat_id, str(target_dir))

        session_manager = SessionManager()
        session_manager.set_working_dir(chat_id, str(target_dir))

        await update.message.reply_text(f"✅ Cloned to:\n`{target_dir}`", parse_mode="Markdown")

    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ Git error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
    except FileNotFoundError:
        await update.message.reply_text("❌ Git is not installed on this server.")


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager
    from bot.services.user_manager import UserManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()
    user_manager = UserManager()

    user = user_manager.get_user(chat_id)
    working_dir = user.working_dir if user and user.working_dir else ""

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


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Operation cancelled.")


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager
    from bot.services.user_manager import UserManager
    import logging
    logger = logging.getLogger(__name__)

    chat_id = update.effective_chat.id

    user_manager = UserManager()
    user = user_manager.get_user(chat_id)
    user_project = user.working_dir if user else ""

    logger.info(f"User project: {user_project}")

    server = ServerFactory.create_opencode(
        url=Settings.OPENCODE_SERVER_URL,
        password=Settings.OPENCODE_SERVER_PASSWORD
    )

    sessions = server.list_sessions()
    logger.info(f"Total sessions: {len(sessions)}")

    if not sessions:
        await update.message.reply_text("No sessions found.")
        return

    user_dir = user_project.rstrip("/") if user_project else ""
    user_dir_basename = Path(user_project).name if user_project else ""

    logger.info(f"Filtering sessions for user_dir: {user_dir}")

    filtered_sessions = []
    for session in sessions:
        directory = session.get("directory", "").rstrip("/")
        title = session.get("title", "")
        logger.info(f"Session: directory={directory}, title={title}")

        match = False
        if user_dir:
            if directory and directory not in ["", "/home/administrador", str(Path.home()).rstrip("/")]:
                if directory.startswith(user_dir) or user_dir.startswith(directory):
                    match = True
            if user_dir_basename and user_dir_basename in title:
                match = True
        else:
            if directory and directory not in ["", "/home/administrador"]:
                match = True

        if match:
            logger.info(f"Session matches: {title}")
            filtered_sessions.append(session)
        else:
            logger.info(f"Session filtered out: {title}")

    if not filtered_sessions:
        if user_project:
            await update.message.reply_text(
                f"No sessions found for:\n{user_project}\n\n"
                "Use /new to create a new session, or use /last."
            )
        else:
            await update.message.reply_text("No TUI sessions found.\nUse /init to set your project first.")
        return

    response_text = "📋 *Sessions*\n\n"

    for session in filtered_sessions[:10]:
        session_id = session.get("id", "")
        title = session.get("title", "")
        project_path = ""

        if title.startswith("BotClaw session for "):
            project_path = title.replace("BotClaw session for ", "").strip()
            if project_path:
                title_clean = Path(project_path).name
            else:
                title_clean = "undefined"
        else:
            title_clean = title.strip() if title.strip() else "undefined"

        response_text += f"• `{session_id}`\n"
        response_text += f"  Title: {title_clean}\n"
        if project_path:
            response_text += f"  Path: {project_path}\n"
        else:
            response_text += f"  Path: undefined\n"

    if not filtered_sessions:
        await update.message.reply_text("No sessions available.")
        return

    response_text += "\n*Tap a button to select, or use `/use <id>` / `/last` *"

    await update.message.reply_text(response_text, parse_mode="Markdown")


async def mcp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.user_manager import UserManager

    chat_id = update.effective_chat.id
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)

    if not user or not user.working_dir:
        await update.message.reply_text("Use /init to set your project first.")
        return

    project_path = Path(user.working_dir)
    skills_dir = project_path / ".agents" / "skills"

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
    import logging
    logger = logging.getLogger(__name__)

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
    session_manager = SessionManager()
    session_manager.set_session_id(chat_id, session_id)

    directory = session_details.get("directory", "")
    if directory:
        session_manager.set_working_dir(chat_id, directory)

    title = session_details.get("title", "Unknown")
    await update.message.reply_text(f"✅ Now using session:\nTitle: {title}\nDir: {directory}")


async def last_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager
    from bot.services.user_manager import UserManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)

    saved_session = session_manager.get_session(chat_id)
    if saved_session.session_id:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )
        if server.continue_session(saved_session.session_id):
            session_manager.set_session_id(chat_id, saved_session.session_id)
            if saved_session.working_dir:
                session_manager.set_working_dir(chat_id, saved_session.working_dir)
            await update.message.reply_text(
                f"✅ Using saved session:\nID: {saved_session.session_id[:20]}\nDir: {saved_session.working_dir}"
            )
            return

    if not user or not user.working_dir:
        await update.message.reply_text("Use /init to set your project directory first.")
        return

    user_dir = user.working_dir.rstrip("/")

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
            f"No sessions found for:\n{user.working_dir}\n\n"
            "Use /new to create a new session."
        )
        return

    if tui_sessions:
        latest_session = tui_sessions[0]
    else:
        latest_session = matching_sessions[0]

    session_id = latest_session.get("id", "")
    title = latest_session.get("title", "Untitled")

    session_manager = SessionManager()
    session_manager.set_session_id(chat_id, session_id)
    session_manager.set_working_dir(chat_id, user.working_dir)

    await update.message.reply_text(f"✅ Connected to latest session:\nTitle: {title}\nDir: {user.working_dir}")


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