import logging
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.servers.factory import ServerFactory

logger = logging.getLogger(__name__)


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    session_manager = SessionManager()

    if args:
        path = " ".join(args)
        full_path = str(Path(path).expanduser().resolve())
    else:
        full_path = session_manager.get_current_path(chat_id)
        if not full_path:
            await update.message.reply_text("No project set. Use /init <path> first or specify a path: /sessions <path>")
            return

    logger.info(f"Listing sessions for: {full_path}")

    try:
        sessions = session_manager.get_sessions_from_api(full_path)

        session_manager.sync_session_dates_from_api(chat_id, full_path)

        if not sessions:
            await update.message.reply_text(
                f"No sessions found for:\n{full_path}\n\n"
                "Use /init to initialize the project."
            )
            return

        response_text = f"📋 *Sessions for* `{full_path}`\n\n"

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

            response_text += f"• Session: `{session_id}`\n"
            title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`").replace("[", r"\[").replace("]", r"\]").replace("(", r"\(").replace(")", r"\)")
            response_text += f"  Title: {title_escaped or 'Untitled'}\n"
            response_text += f"  Created: {created_str}\n"
            response_text += f"  Last access: {last_access_str}\n"

        await update.message.reply_text(response_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text(
            "Usage: /use <session_id>\n"
            "Use /sessions to see available sessions, then copy the session ID."
        )
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
            await update.message.reply_text("❌ Session not found.")
            return

        session_id = session_details.get("id", session_id_prefix)
        directory = session_details.get("directory", "")
        session_manager = SessionManager()
        if directory:
            session_manager.set_session_id(chat_id, directory, session_id)

        title = session_details.get("title", "Unknown")
        title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
        await update.message.reply_text(
            f"✅ Now using session:\n"
            f"Session: `{session_id}`\n"
            f"Title: {title_escaped}\n"
            f"Path: `{directory}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def last_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()

    try:
        saved_session = session_manager.get_current_session(chat_id)
        if saved_session and saved_session.session_id:
            server = ServerFactory.create_opencode(
                url=Settings.OPENCODE_SERVER_URL,
                password=Settings.OPENCODE_SERVER_PASSWORD
            )
            if server.continue_session(saved_session.session_id):
                session_manager.set_session_id(chat_id, saved_session.path, saved_session.session_id)
                try:
                    details = server.get_session_details(saved_session.session_id)
                    title = details.get("title", "") if details else ""
                    title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`") if title else ""
                except Exception:
                    title_escaped = ""

                if title_escaped:
                    msg = (
                        f"✅ Using saved session:\n"
                        f"Session: `{saved_session.session_id}`\n"
                        f"Title: {title_escaped}\n"
                        f"Path: `{saved_session.path}`"
                    )
                else:
                    msg = (
                        f"✅ Using saved session:\n"
                        f"Session: `{saved_session.session_id}`\n"
                        f"Path: `{saved_session.path}`"
                    )
                await update.message.reply_text(msg, parse_mode="Markdown")
                return

        user_dir = session_manager.get_current_path(chat_id)
        if not user_dir:
            await update.message.reply_text("Use /init to set your project directory first.")
            return

        user_dir = user_dir.rstrip("/")

        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        sessions = server.list_sessions()

        matching_sessions = []
        tui_sessions = []
        for session in sessions:
            directory = session.get("directory", "").rstrip("/")
            title = session.get("title", "")
            if directory.startswith(user_dir) or user_dir.startswith(directory):
                if title and not title.startswith("BotClaw session for"):
                    tui_sessions.append(session)
                else:
                    matching_sessions.append(session)

        if not tui_sessions and not matching_sessions:
            await update.message.reply_text(
                f"No sessions found for:\n{user_dir}\n\n"
                "Use /new to create a new session."
            )
            return

        if tui_sessions:
            latest_session = tui_sessions[0]
        else:
            latest_session = matching_sessions[0]

        session_id = latest_session.get("id", "")
        title = latest_session.get("title", "Untitled")
        title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")

        session_manager = SessionManager()
        session_manager.set_session_id(chat_id, user_dir, session_id)

        await update.message.reply_text(
            f"✅ Connected to latest session:\n"
            f"Session: `{session_id}`\n"
            f"Title: {title_escaped}\n"
            f"Path: `{user_dir}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()

    try:
        working_dir = session_manager.get_current_path(chat_id)
        if not working_dir:
            await update.message.reply_text("Set your project first with /init <path>")
            return

        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        session_manager.set_server(server)
        new_session_id = session_manager.create_session_with_dir(chat_id, working_dir)

        if new_session_id:
            await update.message.reply_text(f"✅ New session created:\nSession: `{new_session_id}`\nPath: `{working_dir}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Failed to create new session")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
