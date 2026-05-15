import logging
import sys
from pathlib import Path

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

try:
    from .config.settings import Settings
    from .handlers import commands, messages, callbacks, voice
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from bot.config.settings import Settings
    from bot.handlers import commands, messages, callbacks, voice


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, Settings.LOG_LEVEL)
    )


def main():
    Settings.validate()
    setup_logging()

    Path(Settings.DATA_DIR).mkdir(parents=True, exist_ok=True)

    application = Application.builder().token(Settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", commands.start_command))
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(CommandHandler("status", commands.status_command))
    application.add_handler(CommandHandler("init", commands.init_command))
    application.add_handler(CommandHandler("project", commands.project_command))
    application.add_handler(CommandHandler("projects", commands.projects_command))
    application.add_handler(CommandHandler("clone", commands.clone_command))
    application.add_handler(CommandHandler("new", commands.new_command))
    application.add_handler(CommandHandler("cancel", commands.cancel_command))
    application.add_handler(CommandHandler("sessions", commands.sessions_command))
    application.add_handler(CommandHandler("mcp", commands.mcp_command))
    application.add_handler(CommandHandler("skills", commands.skills_command))
    application.add_handler(CommandHandler("use", commands.use_command))
    application.add_handler(CommandHandler("last", commands.last_command))
    application.add_handler(CommandHandler("voice", commands.voice_command))

    application.add_handler(CallbackQueryHandler(callbacks.handle_callback))

    application.add_handler(MessageHandler(filters.VOICE, voice.handle_voice))
    application.add_handler(MessageHandler(filters.AUDIO, voice.handle_audio))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        messages.handle_message
    ))

    print("🤖 BotClaw starting...")
    print(f"OpenCode Server: {Settings.OPENCODE_SERVER_URL}")

    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()