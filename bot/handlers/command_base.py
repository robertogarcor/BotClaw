import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.i18n import get_available_langs, _
from bot.services.user_manager import UserManager

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user = update.effective_user
    if (Settings.USERS_ALLOWED or Settings.USER_IDS_ALLOWED) and not Settings.is_user_allowed(user.username, user.id):
        await update.message.reply_text(_("auth_denied"))
        return

    user_manager = UserManager()
    db_user = user_manager.get_or_create_user(chat_id, user.username or str(chat_id))
    context.user_data["lang"] = db_user.lang

    await update.message.reply_text(_("welcome", lang=db_user.lang))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = context.user_data.get("lang", "en")
    help_text = (
        _("help_title", lang=lang) + "\n\n"
        + _("help_start_title", lang=lang) + "\n"
        + _("help_start", lang=lang) + "\n\n"
        + _("help_project_title", lang=lang) + "\n"
        + _("help_project", lang=lang) + "\n\n"
        + _("help_sessions_title", lang=lang) + "\n"
        + _("help_sessions", lang=lang) + "\n\n"
        + _("help_voice_title", lang=lang) + "\n"
        + _("help_voice", lang=lang) + "\n\n"
        + _("help_utilities_title", lang=lang) + "\n"
        + _("help_utilities", lang=lang) + "\n\n"
        + _("help_footer", lang=lang)
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_("cancelled", lang=context.user_data.get("lang", "en")))


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args

    lang_aliases = {
        "en": "en", "english": "en",
        "es": "es", "spanish": "es",
    }

    current_lang = context.user_data.get("lang", "en")

    if not args:
        langs = ", ".join(f"`{l}`" for l in get_available_langs())
        await update.message.reply_text(
            _("lang_usage", lang=current_lang)
            + "\n" + _("lang_list", lang=current_lang, langs=langs),
            parse_mode="Markdown"
        )
        return

    raw_arg = args[0].strip().lower()
    new_lang = lang_aliases.get(raw_arg)

    if new_lang is None or new_lang not in get_available_langs():
        await update.message.reply_text(
            _("lang_invalid", lang=current_lang),
            parse_mode="Markdown"
        )
        return

    context.user_data["lang"] = new_lang
    user_manager = UserManager()
    user_manager.set_lang(chat_id, new_lang)

    await update.message.reply_text(
        _("lang_changed", lang=new_lang, lang_code=new_lang.upper()),
        parse_mode="Markdown"
    )
