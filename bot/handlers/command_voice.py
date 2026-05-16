import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


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
