import sqlite3
from pathlib import Path

from bot.config.settings import Settings
from bot.models.user import User


class UserManager:
    def __init__(self):
        self.db_path = Settings.DATABASE_PATH
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                working_dir TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def get_user(self, chat_id: int) -> User:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT chat_id, username, working_dir, created_at FROM users WHERE chat_id = ?",
            (chat_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                chat_id=row["chat_id"],
                username=row["username"],
                working_dir=row["working_dir"] or "",
            )
        return None

    def create_user(self, chat_id: int, username: str) -> User:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO users (chat_id, username) VALUES (?, ?)",
            (chat_id, username)
        )
        conn.commit()
        conn.close()
        return self.get_user(chat_id)

    def set_working_dir(self, chat_id: int, working_dir: str) -> None:
        user = self.get_user(chat_id)
        if not user:
            username = str(chat_id)
            self.create_user(chat_id, username)

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE users SET working_dir = ? WHERE chat_id = ?",
            (working_dir, chat_id)
        )
        conn.commit()
        conn.close()

    def get_or_create_user(self, chat_id: int, username: str) -> User:
        user = self.get_user(chat_id)
        if not user:
            user = self.create_user(chat_id, username)
        return user