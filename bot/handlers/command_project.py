import subprocess
import logging
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.i18n import _
from bot.servers.factory import ServerFactory
from bot.services.session_manager import SessionManager
from bot.services.user_manager import UserManager

logger = logging.getLogger(__name__)


async def project_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text(_("project_not_set", lang=lang))
        return

    project_name = Path(current_path).name
    session = session_manager.get_session(chat_id, current_path)
    current_session_id = session.session_id if session and session.session_id else "None"

    skills_dir = Path(current_path) / ".agents" / "skills"
    skills = []
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir():
                skills.append(item.name)

    response = f"📁 *Project:*\n\n"
    response += _("project_name", lang=lang, name=project_name)
    response += _("project_path", lang=lang, path=current_path)
    response += _("project_session", lang=lang, session=current_session_id)
    if skills:
        response += _("project_skills", lang=lang, skills=', '.join(skills))

    await update.message.reply_text(response, parse_mode="Markdown")


async def projects_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    session_manager = SessionManager()
    base_dir = Path(Settings.PROJECTS_BASE_DIR).expanduser().resolve()

    def is_under_base_dir(raw_path: str) -> bool:
        if not raw_path:
            return False
        try:
            candidate = Path(raw_path).expanduser().resolve()
            return candidate == base_dir or base_dir in candidate.parents
        except Exception:
            return False

    try:
        server = ServerFactory.create_opencode(
            url=Settings.OPENCODE_SERVER_URL,
            password=Settings.OPENCODE_SERVER_PASSWORD
        )

        projects = server._session.get(
            f"{server.url}/project",
            timeout=30
        )

        if projects.status_code != 200:
            await update.message.reply_text(_("projects_api_fail", lang=lang))
            return

        projects_data = projects.json()
        projects_data = [p for p in projects_data if is_under_base_dir(p.get("worktree", ""))]

        sessions = server._session.get(
            f"{server.url}/session",
            timeout=30
        )
        all_sessions = sessions.json() if sessions.status_code == 200 else []

        worktree_to_project = {p.get("worktree"): p for p in projects_data}
        seen_paths = set()

        all_projects = []

        for project in projects_data:
            path = project.get("worktree", "")
            if not path or path in seen_paths:
                continue
            seen_paths.add(path)

            matching_sessions = [
                s for s in all_sessions
                if s.get("directory") == path
            ]
            matching_sessions.sort(key=lambda s: s.get("time", {}).get("updated", 0), reverse=True)

            time_data = project.get("time", {})
            if matching_sessions:
                best_time = matching_sessions[0].get("time", {})
                if best_time.get("updated", 0) > time_data.get("updated", 0):
                    time_data = best_time

            all_projects.append({
                "path": path,
                "time": time_data,
                "sessions": matching_sessions,
            })

        orphan_sessions = [
            s for s in all_sessions
            if s.get("projectID") == "global"
            and s.get("directory")
            and s["directory"] not in worktree_to_project
            and is_under_base_dir(s["directory"])
            and Path(s["directory"]).expanduser().resolve() != base_dir
            and Path(s["directory"]).exists()
        ]

        for s in orphan_sessions:
            dir_path = s["directory"]
            if dir_path in seen_paths:
                continue
            seen_paths.add(dir_path)
            time_data = s.get("time", {})
            all_projects.append({
                "path": dir_path,
                "time": {"created": time_data.get("created", 0), "updated": time_data.get("updated", 0)},
                "sessions": [s],
            })

        if not all_projects:
            base_dir_str = str(base_dir)
            await update.message.reply_text(
                _("projects_none", lang=lang, dir=base_dir_str)
            )
            return

        current_path = session_manager.get_current_path(chat_id)
        active_session = session_manager.get_session(chat_id, current_path) if current_path else None
        active_session_id = active_session.session_id if active_session else None

        response = "📂 *Projects:*\n\n"
        for project in all_projects:
            project_path = project["path"]
            project_name = Path(project_path).name if project_path else "unknown"

            sessions_data = project.get("sessions", [])
            if not sessions_data:
                sessions_data = session_manager.get_sessions_from_api(project_path)
                sessions_data.sort(key=lambda s: s.get("time", {}).get("updated", 0), reverse=True)

            response += _("projects_item_name", lang=lang, name=project_name)
            response += _("projects_item_path", lang=lang, path=project_path)

            if not sessions_data:
                response += _("projects_item_no_session", lang=lang)
            else:
                for i, s in enumerate(sessions_data):
                    sid = s.get("id", "None")
                    s_time = s.get("time", {})
                    s_updated = s_time.get("updated", 0)
                    s_updated_str = datetime.fromtimestamp(s_updated / 1000).strftime("%d-%m-%Y %H:%M") if s_updated else "unknown"
                    s_created = s_time.get("created", 0)
                    s_created_str = datetime.fromtimestamp(s_created / 1000).strftime("%d-%m-%Y %H:%M") if s_created else "unknown"

                    is_active_for_user = sid == active_session_id
                    is_most_recent = i == 0
                    marker = " ✅" if is_active_for_user else (" ➡️" if is_most_recent else "")
                    response += _("projects_item_session", lang=lang, sid=sid, marker=marker)
                    response += _("projects_item_created", lang=lang, date=s_created_str)
                    response += _("projects_item_last_access", lang=lang, date=s_updated_str)

            response += "\n"

        await update.message.reply_text(response[:4096], parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def init_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    args = context.args

    if not args:
        await update.message.reply_text(_("init_usage", lang=lang))
        return

    path = " ".join(args)
    full_path = str(Path(path).expanduser().resolve())

    if not Path(full_path).exists():
        await update.message.reply_text(_("init_path_not_exist", lang=lang, path=full_path))
        return

    session_manager = SessionManager()
    user_manager = UserManager()

    try:
        user_manager.get_or_create_user(chat_id, update.effective_user.username or str(chat_id))

        logger.info(f"Initializing project: {full_path}")
        session_id, is_new, session_data = session_manager.init_project(chat_id, full_path)
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(_("init_error", lang=lang, error=str(e)))
        return
    
    title = session_data.get("title", "") if session_data else ""
    time_data = session_data.get("time", {}) if session_data else {}
    created_ts = time_data.get("created", 0)
    updated_ts = time_data.get("updated", 0)
    
    created_str = datetime.fromtimestamp(created_ts / 1000).strftime("%d-%m-%Y %H:%M") if created_ts else None
    updated_str = datetime.fromtimestamp(updated_ts / 1000).strftime("%d-%m-%Y %H:%M") if updated_ts else None

    project_name = Path(full_path).name
    msg = _("init_success", lang=lang, name=project_name, path=full_path, session=session_id,
            is_new=_("init_new", lang=lang) if is_new else _("init_existing", lang=lang))
    if title:
        title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
        msg += _("status_title", lang=lang, title=title_escaped)
    if created_str:
        msg += _("status_created", lang=lang, date=created_str)
    if updated_str:
        msg += _("status_last_access", lang=lang, date=updated_str)
    msg += _("ready", lang=lang)
    try:
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending /init message: {type(e).__name__}: {e}")


async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    args = context.args

    if not args:
        await update.message.reply_text(_("clone_usage", lang=lang))
        return

    repo_url = args[0]

    is_ssh = repo_url.startswith("git@") or repo_url.startswith("ssh://")
    is_https = repo_url.startswith("https://") or repo_url.startswith("http://")

    if not is_ssh and not is_https:
        await update.message.reply_text(_("clone_invalid_url", lang=lang))
        return

    session_manager = SessionManager()
    user_manager = UserManager()

    current_path = session_manager.get_current_path(chat_id)
    base_dir = str(Path(current_path).parent) if current_path else str(Path.home() / "projects")
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    target_dir = Path(base_dir) / repo_name

    if target_dir.exists():
        await update.message.reply_text(_("clone_dir_exists", lang=lang, dir=str(target_dir)))
        return

    await update.message.reply_text(_("clone_cloning", lang=lang, url=repo_url))

    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(_("clone_git_error", lang=lang, error=e.stderr.decode() if e.stderr else 'Unknown error'))
        return
    except FileNotFoundError:
        await update.message.reply_text(_("clone_git_not_found", lang=lang))
        return

    try:
        user_manager.get_or_create_user(chat_id, update.effective_user.username or str(chat_id))
        session_id, is_new, session_data = session_manager.init_project(chat_id, str(target_dir))
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(_("clone_init_error", lang=lang, dir=str(target_dir), error=str(e)), parse_mode="Markdown")
        return

    msg = _("clone_success", lang=lang, name=repo_name, path=str(target_dir), session=session_id,
            is_new=_("new_session", lang=lang))
    msg += _("ready", lang=lang)
    try:
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending /clone message: {type(e).__name__}: {e}")


async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    lang = context.user_data.get("lang", "en")
    args = context.args

    if not args:
        await update.message.reply_text(_("create_usage", lang=lang))
        return

    raw_path = " ".join(args)

    if raw_path.startswith("/") or raw_path.startswith("~"):
        full_path = str(Path(raw_path).expanduser().resolve())
    else:
        full_path = str(Path(Settings.PROJECTS_BASE_DIR) / raw_path)

    session_manager = SessionManager()
    user_manager = UserManager()

    try:
        user_manager.get_or_create_user(chat_id, update.effective_user.username or str(chat_id))

        logger.info(f"Creating project: {full_path}")
        session_id, is_new, session_data = session_manager.create_project(chat_id, full_path)
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(_("create_error", lang=lang, error=str(e)))
        return

    project_name = Path(full_path).name
    msg = _("create_success", lang=lang, name=project_name, path=full_path, session=session_id,
            is_new=_("new_session", lang=lang))
    msg += _("ready", lang=lang)
    try:
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending /create message: {type(e).__name__}: {e}")
