import os
import logging
import tempfile
from pathlib import Path

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
    user_manager.get_or_create_user(chat_id, user.username)

    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text(
            "Please set your working directory first.\n\n"
            "Use /init <path> to open an existing project\n"
            "Example: /init /home/user/myproject\n\n"
            "Or use /create <name|path> to create a new project\n"
            "Example: /create my-new-project"
        )
        return

    await update.message.reply_text("⏳ Processing...")

    project_prefix = ""
    if current_path:
        project_name = Path(current_path).name
        project_prefix = f"[INFO] Proyecto activo: {project_name} | Directorio: {current_path}. "
        logger.info(f"Sending prompt with project: {project_name}")

    full_prompt = project_prefix + message_text

    session_id = session_manager.get_or_create_session(chat_id, current_path)

    if not session_id:
        await update.message.reply_text("❌ Failed to create session. Ensure OpenCode server is running.")
        return

    logger.info(f"Using session: {session_id}")

    try:
        agent_mode = context.user_data.get("agent_mode")
        response = session_manager.get_server().send_prompt(session_id, full_prompt, agent=agent_mode)

        if response.control_request:
            await update.message.reply_text(
                f"❓ {response.control_request.question}\n\n"
                "Please respond with your answer."
            )
            context.user_data["waiting_for_control_response"] = True
            return

        if response.content:
            voice_mode = context.user_data.get("voice_mode", "off")
            logger.info(f"Message handler - voice_mode: {voice_mode}")
            await send_response_with_voice(update, context, response.content, voice_mode)
        else:
            await update.message.reply_text("✅ Done (no output)")

        session_manager.sync_session_dates_from_api(chat_id, current_path)

    except Exception as e:
        logger.error(f"Error sending prompt: {e}")
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
            voice_mode = context.user_data.get("voice_mode", "off")
            await send_response_with_voice(update, context, response.content, voice_mode)
        else:
            await update.message.reply_text("✅ Done (no output)")

        session_manager.sync_session_dates_from_api(chat_id, session.path)

    except Exception as e:
        logger.error(f"Error in control response: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def send_response_with_voice(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, voice_mode: str) -> None:
    logger.info(f"send_response_with_voice called with voice_mode: {voice_mode}")
    if voice_mode == "on":
        try:
            from bot.services.tts import synthesize_to_opus
            from bot.services.audio_utils import cleanup_temp_files

            logger.info("Generating TTS audio...")
            temp_dir = tempfile.gettempdir()
            audio_path = await synthesize_to_opus(text, temp_dir)
            logger.info(f"TTS result: {audio_path}")

            if audio_path and os.path.exists(audio_path):
                await update.message.reply_voice(audio_path)
                cleanup_temp_files(audio_path)
                logger.info(f"Sent voice response")
                await update.message.reply_text(f"📝 Transcript: {text[:4096]}", parse_mode="Markdown")
                return

        except Exception as e:
            logger.error(f"TTS failed: {e}, falling back to text")

    logger.info("Sending text response (fallback)")
    await update.message.reply_text(text[:4096])
