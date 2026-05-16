import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings

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
        "/init <path> - Set working directory\n\n"
        
        "📁 *Project*\n"
        "/create <path> - Create new project directory\n"
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
        "/status - Show current status\n"
        "/mcp - Show MCP servers\n"
        "/skills - Show project skills\n"
        "/cancel - Cancel current operation\n\n"
        
        "_Just send me a message or voice to chat with OpenCode!_"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Operation cancelled.")
