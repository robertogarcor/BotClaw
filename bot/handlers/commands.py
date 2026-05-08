import subprocess
from pathlib import Path
from telegram import Update
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
        "📖 *Available Commands*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/init <path> - Set your working directory\n"
        "/clone <url> - Clone a git repository\n"
        "/cd <path> - Change working directory\n"
        "/new - Start a new session\n"
        "/status - Show current project info\n"
        "/sessions - List OpenCode sessions\n"
        "/mcp - Show MCP servers\n"
        "/cancel - Cancel current operation\n\n"
        "Just send me a message to start chatting with OpenCode!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.user_manager import UserManager

    chat_id = update.effective_chat.id
    user_manager = UserManager()
    user = user_manager.get_user(chat_id)

    if not user:
        await update.message.reply_text("Use /init first to set up your project.")
        return

    status_text = f"📁 *Status*\n\n"
    status_text += f"Working Dir: `{user.working_dir or 'Not set'}`\n"

    if user.working_dir and Path(user.working_dir).exists():
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=user.working_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                status_text += f"Git Repo: ✅\n"
            else:
                status_text += f"Git Repo: ❌\n"
        except FileNotFoundError:
            status_text += f"Git: ❌ (not installed)\n"
    else:
        status_text += f"Git Repo: ❌\n"

    await update.message.reply_text(status_text, parse_mode="Markdown")


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
    session_manager.set_working_dir(chat_id, full_path)

    await update.message.reply_text(f"✅ Working directory set to:\n`{full_path}`", parse_mode="Markdown")


async def cd_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await init_command(update, context)


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
        await update.message.reply_text(f"📁 Directory already exists: {target_dir}\nUse /cd {target_dir} to use it.")
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

    chat_id = update.effective_chat.id
    session_manager = SessionManager()

    server = ServerFactory.create_opencode(
        url=Settings.OPENCODE_SERVER_URL,
        password=Settings.OPENCODE_SERVER_PASSWORD
    )

    session_manager.set_server(server)
    new_session_id = session_manager.create_session(chat_id)

    if new_session_id:
        await update.message.reply_text(f"✅ New session created!")
    else:
        await update.message.reply_text("❌ Failed to create new session")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Operation cancelled.")


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    server = ServerFactory.create_opencode(
        url=Settings.OPENCODE_SERVER_URL,
        password=Settings.OPENCODE_SERVER_PASSWORD
    )

    sessions = server.list_sessions()

    if not sessions:
        await update.message.reply_text("No sessions found.")
        return

    response_text = "📋 *Sessions:*\n\n"
    for session in sessions[:10]:
        session_id = session.get("id", "")
        title = session.get("title", "Untitled")
        directory = session.get("directory", "")
        response_text += f"• `{session_id[:20]}...`\n"
        response_text += f"  Title: {title}\n"
        if directory:
            response_text += f"  Dir: {directory}\n"
        response_text += "\n"

    await update.message.reply_text(response_text[:4096], parse_mode="Markdown")


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