import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.i18n import _
from bot.handlers.command_base import help_command
from bot.handlers.command_info import status_command
from bot.handlers.command_sessions import new_command
from bot.servers.factory import ServerFactory
from bot.services.session_manager import SessionManager

logger = logging.getLogger(__name__)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "new_session":
        await new_command(update, context)
    elif data == "status":
        await status_command(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data.startswith("session:"):
        session_id = data.split(":", 1)[1]
        await select_session_from_callback(update, context, session_id)


async def select_session_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: str) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")

    server = ServerFactory.create_opencode(
        url=Settings.OPENCODE_SERVER_URL,
        password=Settings.OPENCODE_SERVER_PASSWORD
    )

    session_details = server.get_session_details(session_id)

    if not session_details:
        await update.callback_query.edit_message_text(_("session_not_found", lang=lang))
        return

    session_manager = SessionManager()

    directory = session_details.get("directory", "")
    if directory:
        session_manager.save_session(chat_id, directory, session_id)

    title = session_details.get("title", "Unknown")
    title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
    await update.callback_query.edit_message_text(
        _("callback_session_selected", lang=lang, id=session_id, title=title_escaped, dir=directory)
    )
