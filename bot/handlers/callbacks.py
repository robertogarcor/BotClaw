from telegram import Update
from telegram.ext import ContextTypes


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "new_session":
        from bot.handlers.commands import new_command
        await new_command(update, context)
    elif data == "status":
        from bot.handlers.commands import status_command
        await status_command(update, context)
    elif data == "help":
        from bot.handlers.commands import help_command
        await help_command(update, context)
    elif data.startswith("session:"):
        session_id = data.split(":", 1)[1]
        await select_session_from_callback(update, context, session_id)


async def select_session_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: str) -> None:
    from bot.services.session_manager import SessionManager
    from bot.servers.factory import ServerFactory
    from bot.config.settings import Settings
    import logging

    logger = logging.getLogger(__name__)
    chat_id = update.effective_chat.id

    server = ServerFactory.create_opencode(
        url=Settings.OPENCODE_SERVER_URL,
        password=Settings.OPENCODE_SERVER_PASSWORD
    )

    session_details = server.get_session_details(session_id)

    if not session_details:
        await update.callback_query.edit_message_text("❌ Session not found.")
        return

    session_manager = SessionManager()

    directory = session_details.get("directory", "")
    if directory:
        session_manager.save_session(chat_id, directory, session_id)

    title = session_details.get("title", "Unknown")
    await update.callback_query.edit_message_text(
        f"✅ Now using session:\nTitle: {title}\nDir: {directory}"
    )