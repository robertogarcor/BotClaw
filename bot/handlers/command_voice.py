import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.i18n import _

logger = logging.getLogger(__name__)


async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    args = context.args

    if not args:
        current = context.user_data.get("voice_mode", "off")
        new_mode = "off" if current == "on" else "on"
        context.user_data["voice_mode"] = new_mode
        if new_mode == "on":
            await update.message.reply_text(_("voice_on", lang=lang))
        else:
            await update.message.reply_text(_("voice_off", lang=lang))
        return

    subcommand = args[0].lower()

    if subcommand == "on":
        context.user_data["voice_mode"] = "on"
        await update.message.reply_text(_("voice_on", lang=lang))

    elif subcommand == "off":
        context.user_data["voice_mode"] = "off"
        await update.message.reply_text(_("voice_off", lang=lang))

    elif subcommand == "status":
        mode = context.user_data.get("voice_mode", "off")
        await update.message.reply_text(_("voice_status", lang=lang, mode=mode), parse_mode="Markdown")

    else:
        await update.message.reply_text(_("voice_usage", lang=lang))
