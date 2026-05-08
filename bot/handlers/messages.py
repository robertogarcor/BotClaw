import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.services.user_manager import UserManager
from bot.services.session_manager import SessionManager
from bot.servers.factory import ServerFactory

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = None) -> None:
    user = update.effective_user
    if (Settings.USERS_ALLOWED or Settings.USER_IDS_ALLOWED) and not Settings.is_user_allowed(user.username, user.id):
        return

    chat_id = update.effective_chat.id
    message_text = text if text is not None else update.message.text

    if not message_text:
        return

    user_manager = UserManager()
    user_obj = user_manager.get_or_create_user(chat_id, user.username)

    if not user_obj.working_dir:
        await update.message.reply_text(
            "Please set your working directory first using /init <path>\n"
            "Example: /init /home/user/myproject"
        )
        return

    await update.message.reply_text("⏳ Processing...")

    session_manager = SessionManager()

    session_id = session_manager.get_or_create_session(chat_id)

    if not session_id:
        await update.message.reply_text("❌ Failed to create session. Ensure OpenCode server is running.")
        return

    logger.info(f"Using session: {session_id}")

    try:
        response = session_manager.get_server().send_prompt(session_id, message_text)

        if response.control_request:
            await update.message.reply_text(
                f"❓ {response.control_request.question}\n\n"
                "Please respond with your answer."
            )
            context.user_data["waiting_for_control_response"] = True
            return

        if response.content:
            await update.message.reply_text(response.content[:4096])
        else:
            await update.message.reply_text("✅ Done (no output)")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_control_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("waiting_for_control_response"):
        return

    context.user_data["waiting_for_control_response"] = False
    chat_id = update.effective_chat.id
    response_text = update.message.text

    session_manager = SessionManager()

    session = session_manager.get_session(chat_id)
    if not session.session_id:
        await update.message.reply_text("❌ No active session")
        return

    await update.message.reply_text("⏳ Processing your response...")

    try:
        response = session_manager.get_server().send_control_response(session.session_id, response_text)

        if response.control_request:
            await update.message.reply_text(
                f"❓ {response.control_request.question}\n\n"
                "Please respond with your answer."
            )
            context.user_data["waiting_for_control_response"] = True
            return

        if response.content:
            await update.message.reply_text(response.content[:4096])
        else:
            await update.message.reply_text("✅ Done (no output)")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")