import logging
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.i18n import _
from bot.servers.factory import ServerFactory
from bot.services.session_manager import SessionManager

logger = logging.getLogger(__name__)


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    args = context.args

    session_manager = SessionManager()

    if args:
        path = " ".join(args)
        full_path = str(Path(path).expanduser().resolve())
    else:
        full_path = session_manager.get_current_path(chat_id)
        if not full_path:
            await update.message.reply_text(_("sessions_no_project", lang=lang))
            return

    logger.info(f"Listing sessions for: {full_path}")

    try:
        sessions = session_manager.get_sessions_from_api(full_path)

        session_manager.sync_session_dates_from_api(chat_id, full_path)

        if not sessions:
            await update.message.reply_text(_("sessions_none", lang=lang, path=full_path))
            return

        response_text = _("sessions_header", lang=lang, path=full_path)

        for session in sessions[:10]:
            session_id = session.get("id", "")
            title = session.get("title", "")
            time_data = session.get("time", {})
            created = time_data.get("created", 0)
            updated = time_data.get("updated", 0)
            
            if created:
                created_str = datetime.fromtimestamp(created / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                created_str = "unknown"
            
            if updated:
                last_access_str = datetime.fromtimestamp(updated / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                last_access_str = "unknown"

            response_text += _("sessions_item", lang=lang, id=session_id)
            title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`").replace("[", r"\[").replace("]", r"\]").replace("(", r"\(").replace(")", r"\)")
            response_text += _("sessions_item_title", lang=lang, title=title_escaped or 'Untitled')
            response_text += _("sessions_item_created", lang=lang, date=created_str)
            response_text += _("sessions_item_last_access", lang=lang, date=last_access_str)

        await update.message.reply_text(response_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    args = context.args

    if not args:
        await update.message.reply_text(_("use_usage", lang=lang))
        return

    session_id_prefix = args[0].strip()
    logger.info(f"use_command: trying session_id={session_id_prefix}")

    try:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        session_details = server.get_session_details(session_id_prefix)

        if not session_details:
            sessions = server.list_sessions()
            for session in sessions:
                if session.get("id", "").startswith(session_id_prefix):
                    session_id = session.get("id", "")
                    session_details = server.get_session_details(session_id)
                    logger.info(f"use_command: found by prefix: {session_id}")
                    break

        if not session_details:
            await update.message.reply_text(_("session_not_found", lang=lang))
            return

        session_id = session_details.get("id", session_id_prefix)
        directory = session_details.get("directory", "")
        session_manager = SessionManager()
        current_path = session_manager.get_current_path(chat_id)

        if directory and current_path and directory != current_path:
            await update.message.reply_text(
                _("session_wrong_project", lang=lang, dir=directory),
                parse_mode="Markdown"
            )
            return

        if directory:
            session_manager.set_session_id(chat_id, directory, session_id)

        title = session_details.get("title", "Unknown")
        title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
        await update.message.reply_text(
            _("session_selected", lang=lang, id=session_id, title=title_escaped, dir=directory),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def last_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    session_manager = SessionManager()

    try:
        user_dir = session_manager.get_current_path(chat_id)
        if not user_dir:
            await update.message.reply_text(_("last_no_project", lang=lang))
            return

        user_dir = user_dir.rstrip("/")

        sessions = session_manager.get_sessions_from_api(user_dir)

        if not sessions:
            await update.message.reply_text(_("last_no_sessions", lang=lang, path=user_dir))
            return

        sessions.sort(key=lambda x: x.get("time", {}).get("updated", 0), reverse=True)
        latest_session = sessions[0]

        session_id = latest_session.get("id", "")
        title = latest_session.get("title", "Untitled")
        title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")

        session_manager.set_session_id(chat_id, user_dir, session_id)

        await update.message.reply_text(
            _("last_connected", lang=lang, id=session_id, title=title_escaped, path=user_dir),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    session_manager = SessionManager()

    try:
        working_dir = session_manager.get_current_path(chat_id)
        if not working_dir:
            await update.message.reply_text(_("new_no_project", lang=lang))
            return

        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        session_manager.set_server(server)
        new_session_id = session_manager.create_session_with_dir(chat_id, working_dir)

        if new_session_id:
            await update.message.reply_text(_("new_created", lang=lang, id=new_session_id, path=working_dir), parse_mode="Markdown")
        else:
            await update.message.reply_text(_("new_failed", lang=lang))
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def rename_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    args = context.args

    if not args:
        await update.message.reply_text(_("rename_usage", lang=lang))
        return

    new_title = " ".join(args)

    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)
    if not current_path:
        await update.message.reply_text(_("rename_no_project", lang=lang))
        return

    session = session_manager.get_session(chat_id, current_path)
    if not session or not session.session_id:
        await update.message.reply_text(_("rename_no_session", lang=lang))
        return

    try:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        success = server.rename_session(session.session_id, new_title)

        if success:
            title_escaped = new_title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
            await update.message.reply_text(
                _("rename_success", lang=lang, id=session.session_id, title=title_escaped),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(_("rename_failed", lang=lang))
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
