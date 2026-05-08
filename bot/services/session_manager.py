import sqlite3
from pathlib import Path
from typing import Optional

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
                chat_id INTEGER PRIMARY KEY,
                session_id TEXT,
                working_dir TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def get_session(self, chat_id: int) -> Session:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT chat_id, session_id, working_dir, created_at FROM sessions WHERE chat_id = ?",
            (chat_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return Session(
                chat_id=row["chat_id"],
                session_id=row["session_id"] or "",
                working_dir=row["working_dir"] or "",
            )
        return Session(chat_id=chat_id)

    def create_session(self, chat_id: int) -> str:
        session = self.get_session(chat_id)
        working_dir = session.working_dir

        server = self._get_server()
        session_id = server.create_session(working_dir)

        if session_id:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO sessions (chat_id, session_id, working_dir) VALUES (?, ?, ?)",
                (chat_id, session_id, working_dir)
            )
            conn.commit()
            conn.close()

        return session_id

    def set_working_dir(self, chat_id: int, working_dir: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT session_id, working_dir FROM sessions WHERE chat_id = ?",
            (chat_id,)
        )
        row = cursor.fetchone()

        if row and row[0]:
            session_id = row[0]
            conn.execute(
                "UPDATE sessions SET working_dir = ? WHERE chat_id = ?",
                (working_dir, chat_id)
            )
        else:
            session_id = self._get_server().create_session(working_dir)
            conn.execute(
                "INSERT OR REPLACE INTO sessions (chat_id, session_id, working_dir) VALUES (?, ?, ?)",
                (chat_id, session_id, working_dir)
            )

        conn.commit()
        conn.close()

    def set_session_id(self, chat_id: int, session_id: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT working_dir FROM sessions WHERE chat_id = ?",
            (chat_id,)
        )
        row = cursor.fetchone()
        working_dir = row[0] if row else ""

        conn.execute(
            "INSERT OR REPLACE INTO sessions (chat_id, session_id, working_dir) VALUES (?, ?, ?)",
            (chat_id, session_id, working_dir)
        )
        conn.commit()
        conn.close()

    def get_or_create_session(self, chat_id: int) -> str:
        session = self.get_session(chat_id)
        if session.session_id:
            server = self._get_server()
            if server.continue_session(session.session_id):
                return session.session_id

        return self.create_session(chat_id)

    def clear_session(self, chat_id: int) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM sessions WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()