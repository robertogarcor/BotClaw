import subprocess
import logging
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import Settings
from bot.servers.factory import ServerFactory

logger = logging.getLogger(__name__)


async def project_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()
    current_path = session_manager.get_current_path(chat_id)

    if not current_path:
        await update.message.reply_text("📁 *Project:*\n\nNo project set.\nUse `/init <path>` to set your project.")
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
    response += f"Name: `{project_name}`\n"
    response += f"Path: `{current_path}`\n"
    response += f"Session: `{current_session_id}`\n"
    if skills:
        response += f"Skills: {', '.join(skills)}"

    await update.message.reply_text(response, parse_mode="Markdown")


async def projects_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    session_manager = SessionManager()

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
            await update.message.reply_text("📂 *Projects:*\n\nFailed to fetch projects from API.")
            return

        projects_data = projects.json()
        projects_data = [p for p in projects_data if p.get("id") != "global"]

        sessions = server._session.get(
            f"{server.url}/session",
            timeout=30
        )

        global_projects = {}
        if sessions.status_code == 200:
            base_dir = str(Path(Settings.PROJECTS_BASE_DIR).expanduser().resolve())
            home_dir = str(Path.home())
            for s in sessions.json():
                if s.get("projectID") == "global" and s.get("directory"):
                    dir_path = s["directory"]
                    if dir_path in (base_dir, home_dir):
                        continue
                    if dir_path not in global_projects:
                        global_projects[dir_path] = s

        registered_paths = {p.get("worktree") for p in projects_data}
        global_projects = {k: v for k, v in global_projects.items() if k not in registered_paths}

        all_projects = []
        for project in projects_data:
            all_projects.append({
                "path": project.get("worktree", ""),
                "time": project.get("time", {}),
                "session_id": None,
            })

        for dir_path, session in global_projects.items():
            time_data = session.get("time", {})
            all_projects.append({
                "path": dir_path,
                "time": {"created": time_data.get("created", 0), "updated": time_data.get("updated", 0)},
                "session_id": session.get("id", "None"),
            })

        if not all_projects:
            await update.message.reply_text("📂 *Projects:*\n\nNo projects found.\nUse `/init <path>` to start.")
            return

        response = "📂 *Projects:*\n\n"
        for project in all_projects:
            project_path = project["path"]
            time_data = project["time"]
            created_ts = time_data.get("created", 0)
            updated_ts = time_data.get("updated", 0)

            if created_ts:
                created_str = datetime.fromtimestamp(created_ts / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                created_str = "unknown"

            if updated_ts:
                last_access_str = datetime.fromtimestamp(updated_ts / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                last_access_str = "unknown"

            session_id = project["session_id"]
            if not session_id:
                sessions_list = session_manager.get_sessions_from_api(project_path)
                session_id = sessions_list[0].get("id", "None") if sessions_list else "None"

            project_name = Path(project_path).name if project_path else "unknown"

            response += f"• *{project_name}*\n"
            response += f"  Path: `{project_path}`\n"
            response += f"  Session: `{session_id}`\n"
            response += f"  Created: {created_str}\n"
            response += f"  Last access: {last_access_str}\n\n"

        await update.message.reply_text(response[:4096], parse_mode="Markdown")
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def init_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.user_manager import UserManager
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text("Usage: /init <path>\nExample: /init /home/user/myproject")
        return

    path = " ".join(args)
    full_path = str(Path(path).expanduser().resolve())

    if not Path(full_path).exists():
        await update.message.reply_text(f"❌ Path does not exist: {full_path}")
        return

    session_manager = SessionManager()
    user_manager = UserManager()

    try:
        user_manager.get_or_create_user(chat_id, update.effective_user.username or str(chat_id))

        logger.info(f"Initializing project: {full_path}")
        session_id, is_new, session_data = session_manager.init_project(chat_id, full_path)
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error initializing project: {str(e)}")
        return
    
    title = session_data.get("title", "") if session_data else ""
    time_data = session_data.get("time", {}) if session_data else {}
    created_ts = time_data.get("created", 0)
    updated_ts = time_data.get("updated", 0)
    
    created_str = datetime.fromtimestamp(created_ts / 1000).strftime("%d-%m-%Y %H:%M") if created_ts else None
    updated_str = datetime.fromtimestamp(updated_ts / 1000).strftime("%d-%m-%Y %H:%M") if updated_ts else None

    logger.info("Checking for AGENTS.md and SPEC.md...")
    agents_path = Path(full_path) / "AGENTS.md"
    spec_path = Path(full_path) / "SPEC.md"

    context_loaded = []
    context_text = ""

    if agents_path.exists():
        try:
            agents_content = agents_path.read_text()
            context_text += f"--- AGENTS.md ---\n{agents_content}\n"
            context_loaded.append("AGENTS.md")
        except Exception:
            pass

    if spec_path.exists():
        try:
            spec_content = spec_path.read_text()
            context_text += f"\n--- SPEC.md ---\n{spec_content}\n"
            context_loaded.append("SPEC.md")
        except Exception:
            pass

    session = session_manager.get_session(chat_id, full_path)
    if session and session.session_id and context_text:
        await update.message.reply_text("⏳ Loading project context...")
        try:
            server = session_manager.get_server()
            project_name = Path(full_path).name
            prompt = (
                f"IMPORTANTE: Proyecto actual = {project_name}\n"
                f"Directorio de trabajo: {full_path}\n\n"
                f"Contexto del proyecto:\n{context_text}\n\n"
                f"Este es el único proyecto activo. Olvida cualquier proyecto anterior."
            )
            response = server.send_prompt(session.session_id, prompt)
            logger.info(f"Context loaded, response received")
        except Exception as e:
            logger.error(f"Failed to load context: {e}")

    if context_loaded:
        project_name = Path(full_path).name
        msg = f"✅ *{project_name}* configurado\n\n"
        msg += f"Path: `{full_path}`\n"
        msg += f"Session: `{session_id}`\n"
        if is_new:
            msg += "🆕 Nueva sesión creada\n"
        else:
            msg += "🔄 Sesión existente reutilizada\n"
        if title:
            title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
            msg += f"Title: {title_escaped}\n"
        if created_str:
            msg += f"Created: {created_str}\n"
        if updated_str:
            msg += f"Last access: {updated_str}\n"
        msg += f"📄 Context: {', '.join(context_loaded)}\n\n"
        msg += f"*Listo para recibir mensajes.*"
        try:
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending /init message: {type(e).__name__}: {e}")
    else:
        project_name = Path(full_path).name
        msg = f"✅ *{project_name}* configurado\n\n"
        msg += f"Path: `{full_path}`\n"
        msg += f"Session: `{session_id}`\n"
        if is_new:
            msg += "🆕 Nueva sesión creada\n"
        else:
            msg += "🔄 Sesión existente reutilizada\n"
        if title:
            title_escaped = title.replace("_", r"\_").replace("*", r"\*").replace("`", r"\`")
            msg += f"Title: {title_escaped}\n"
        if created_str:
            msg += f"Created: {created_str}\n"
        if updated_str:
            msg += f"Last access: {updated_str}\n"
        msg += f"\n*Listo para recibir mensajes.*"
        try:
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending /init message: {type(e).__name__}: {e}")


async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text("Usage: /clone <repo_url>\nExample: /clone https://github.com/user/repo.git")
        return

    repo_url = args[0]
    session_manager = SessionManager()

    current_path = session_manager.get_current_path(chat_id)
    base_dir = str(Path(current_path).parent) if current_path else str(Path.home() / "projects")
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    target_dir = Path(base_dir) / repo_name

    if target_dir.exists():
        await update.message.reply_text(f"📁 Directory already exists: {target_dir}\nUse /init {target_dir} to use it.")
        return

    await update.message.reply_text(f"🔄 Cloning {repo_url}...")

    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            check=True,
            capture_output=True
        )

        await update.message.reply_text(f"✅ Cloned to:\n`{target_dir}`\n\nUse /init {target_dir} to start working with it.", parse_mode="Markdown")

    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ Git error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
    except FileNotFoundError:
        await update.message.reply_text("❌ Git is not installed on this server.")


async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from bot.services.user_manager import UserManager
    from bot.services.session_manager import SessionManager

    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text("Usage: /create <name|path>\nExample: /create myproject or /create /home/user/myproject")
        return

    raw_path = " ".join(args)

    if raw_path.startswith("/") or raw_path.startswith("~"):
        full_path = str(Path(raw_path).expanduser().resolve())
    else:
        full_path = str(Path(Settings.PROJECTS_BASE_DIR) / raw_path)

    if Path(full_path).exists():
        await update.message.reply_text(f"📁 Directory already exists: {full_path}\nUse /init {full_path} to use it.")
        return

    try:
        Path(full_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to create directory: {str(e)}")
        return

    session_manager = SessionManager()
    user_manager = UserManager()

    try:
        user_manager.get_or_create_user(chat_id, update.effective_user.username or str(chat_id))

        logger.info(f"Creating project: {full_path}")
        session_id, is_new, session_data = session_manager.init_project(chat_id, full_path)
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        await update.message.reply_text(f"❌ Error creating project: {str(e)}")
        return

    project_name = Path(full_path).name
    msg = (
        f"✅ *{project_name}* created and configured\n\n"
        f"Path: `{full_path}`\n"
        f"Session: `{session_id}`\n\n"
        f"*Listo para recibir mensajes.*"
    )
    try:
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending /create message: {type(e).__name__}: {e}")
