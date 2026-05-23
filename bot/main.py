import logging
import sys
from pathlib import Path

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

try:
    from .config.settings import Settings
    from .handlers import command_base, command_project, command_sessions, command_info, command_voice
    from .handlers import messages, callbacks, voice
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from bot.config.settings import Settings
    from bot.handlers import command_base, command_project, command_sessions, command_info, command_voice
    from bot.handlers import messages, callbacks, voice


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

    application.add_handler(CommandHandler("start", command_base.start_command))
    application.add_handler(CommandHandler("help", command_base.help_command))
    application.add_handler(CommandHandler("status", command_info.status_command))
    application.add_handler(CommandHandler("mode", command_info.mode_command))
    application.add_handler(CommandHandler("init", command_project.init_command))
    application.add_handler(CommandHandler("project", command_project.project_command))
    application.add_handler(CommandHandler("projects", command_project.projects_command))
    application.add_handler(CommandHandler("clone", command_project.clone_command))
    application.add_handler(CommandHandler("create", command_project.create_command))
    application.add_handler(CommandHandler("new", command_sessions.new_command))
    application.add_handler(CommandHandler("cancel", command_base.cancel_command))
    application.add_handler(CommandHandler("lang", command_base.lang_command))
    application.add_handler(CommandHandler("sessions", command_sessions.sessions_command))
    application.add_handler(CommandHandler("mcp", command_info.mcp_command))
    application.add_handler(CommandHandler("skills", command_info.skills_command))
    application.add_handler(CommandHandler("use", command_sessions.use_command))
    application.add_handler(CommandHandler("last", command_sessions.last_command))
    application.add_handler(CommandHandler("rename", command_sessions.rename_command))
    application.add_handler(CommandHandler("voice", command_voice.voice_command))

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
