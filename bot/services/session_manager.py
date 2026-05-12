import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from bot.config.settings import Settings
from bot.models.session import Session
from bot.servers.base import BaseServer


class SessionManager:
    def __init__(self):
        self.db_path = Settings.DATABASE_PATH
        self._server: Optional[BaseServer] = None
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                chat_id INTEGER,
                path TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, path)
            )
        """)
        conn.commit()
        conn.close()

    def set_server(self, server: BaseServer) -> None:
        self._server = server

    def get_server(self) -> BaseServer:
        return self._get_server()

    def _get_server(self) -> BaseServer:
        if not self._server:
            from bot.servers.factory import ServerFactory
            self._server = ServerFactory.create_opencode(
                url=Settings.OPENCODE_SERVER_URL,
                password=Settings.OPENCODE_SERVER_PASSWORD
            )
        return self._server

    def get_session(self, chat_id: int, path: str = None) -> Optional[Session]:
        if not path:
            return None
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT chat_id, path, session_id, created_at, updated_at, last_access FROM sessions WHERE chat_id = ? AND path = ?",
            (chat_id, path)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return Session(
                chat_id=row["chat_id"],
                path=row["path"],
                session_id=row["session_id"] or "",
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                last_access=row["last_access"],
            )
        return None

    def get_sessions_from_api(self, path: str) -> List[dict]:
        if not path:
            return []
        
        server = self._get_server()
        
        try:
            response = server._session.get(
                f"{server.url}/session",
                params={"directory": path},
                timeout=30
            )
            if response.status_code == 200:
                sessions = response.json()
                return sessions if isinstance(sessions, list) else []
        except Exception:
            pass
        
        return []

    def save_session(self, chat_id: int, path: str, session_id: str) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO sessions (chat_id, path, session_id, updated_at, last_access)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (chat_id, path, session_id))
        conn.commit()
        conn.close()

    def update_last_access(self, chat_id: int, path: str) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE sessions SET last_access = CURRENT_TIMESTAMP WHERE chat_id = ? AND path = ?",
            (chat_id, path)
        )
        conn.commit()
        conn.close()

    def init_project(self, chat_id: int, path: str) -> tuple[str, bool]:
        path = path.rstrip("/")
        server = self._get_server()
        
        api_sessions = self.get_sessions_from_api(path)
        
        if api_sessions:
            api_sessions.sort(key=lambda x: x.get("time", {}).get("updated", 0), reverse=True)
            session_id = api_sessions[0].get("id")
            self.save_session(chat_id, path, session_id)
            return session_id, False
        
        response = server._session.post(
            f"{server.url}/session",
            json={"title": f"BotClaw session for {path}"},
            timeout=30
        )
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            session_id = data.get("id", "")
        elif response.status_code == 204:
            session_id = "default"
        else:
            session_id = ""
        
        if session_id:
            self.save_session(chat_id, path, session_id)
        
        return session_id, True

    def get_or_create_session(self, chat_id: int, path: str) -> str:
        session = self.get_session(chat_id, path)
        if session and session.session_id:
            self.update_last_access(chat_id, path)
            return session.session_id
        
        session_id, _ = self.init_project(chat_id, path)
        return session_id

    def set_session_id(self, chat_id: int, path: str, session_id: str) -> None:
        self.save_session(chat_id, path, session_id)

    def clear_session(self, chat_id: int, path: str = None) -> None:
        conn = sqlite3.connect(self.db_path)
        if path:
            conn.execute("DELETE FROM sessions WHERE chat_id = ? AND path = ?", (chat_id, path))
        else:
            conn.execute("DELETE FROM sessions WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()

    def get_current_path(self, chat_id: int) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT path FROM sessions WHERE chat_id = ? ORDER BY last_access DESC LIMIT 1",
            (chat_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row["path"] if row else None

    def get_current_session(self, chat_id: int) -> Optional[Session]:
        path = self.get_current_path(chat_id)
        if path:
            return self.get_session(chat_id, path)
        return None
