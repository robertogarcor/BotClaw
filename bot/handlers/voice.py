import os
import tempfile
import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.services.audio_utils import download_voice, download_audio, cleanup_temp_files
from bot.services.stt import transcribe_local
from bot.handlers import messages

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if (Settings.USERS_ALLOWED or Settings.USER_IDS_ALLOWED) and not Settings.is_user_allowed(user.username, user.id):
        return

    await update.message.reply_text("🎤 Processing voice message...")

    voice = update.message.voice
    if not voice:
        return

    temp_dir = tempfile.gettempdir()
    audio_path = ""

    try:
        audio_path = await download_voice(context.bot, voice.file_id, temp_dir)

        if not audio_path or not os.path.exists(audio_path):
            await update.message.reply_text("❌ Failed to download voice message.")
            return

        text = transcribe_local(audio_path)

        if not text.strip():
            await update.message.reply_text("❌ Could not understand the audio.")
            return

        logger.info(f"Transcribed: {text[:100]}...")
        await update.message.reply_text(f"📝 Transcribed: {text}")

        await messages.handle_message(update, context, text)

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await update.message.reply_text(f"❌ Error processing voice: {str(e)}")

    finally:
        if audio_path:
            cleanup_temp_files(audio_path)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if (Settings.USERS_ALLOWED or Settings.USER_IDS_ALLOWED) and not Settings.is_user_allowed(user.username, user.id):
        return

    await update.message.reply_text("🎵 Processing audio...")

    audio = update.message.audio
    if not audio:
        return

    temp_dir = tempfile.gettempdir()
    audio_path = ""

    try:
        audio_path = await download_audio(context.bot, audio.file_id, temp_dir)

        if not audio_path or not os.path.exists(audio_path):
            await update.message.reply_text("❌ Failed to download audio.")
            return

        text = transcribe_local(audio_path)

        if not text.strip():
            await update.message.reply_text("❌ Could not transcribe the audio.")
            return

        logger.info(f"Transcribed audio: {text[:100]}...")
        await update.message.reply_text(f"📝 Transcribed: {text}")

        await messages.handle_message(update, context, text)

    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await update.message.reply_text(f"❌ Error processing audio: {str(e)}")

    finally:
        if audio_path:
            cleanup_temp_files(audio_path)