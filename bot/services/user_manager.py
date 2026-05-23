import logging
import sqlite3
from pathlib import Path

from bot.config.settings import Settings
from bot.models.user import User

logger = logging.getLogger(__name__)


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
                voice_mode TEXT DEFAULT 'off',
                lang TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            conn.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'en'")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.close()

    def get_user(self, chat_id: int) -> User:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT chat_id, username, voice_mode, lang, created_at FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            row = cursor.fetchone()

            if row:
                return User(
                    chat_id=row["chat_id"],
                    username=row["username"] or "",
                    voice_mode=row["voice_mode"] or "off",
                    lang=row["lang"] or "en",
                    created_at=row["created_at"],
                )
            return None
        except sqlite3.Error as e:
            logger.error(f"DB error in get_user: {type(e).__name__}: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def create_user(self, chat_id: int, username: str) -> User:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT OR IGNORE INTO users (chat_id, username, voice_mode, lang) VALUES (?, ?, 'off', 'en')",
                (chat_id, username)
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"DB error in create_user: {type(e).__name__}: {e}")
        finally:
            if conn:
                conn.close()
        return self.get_user(chat_id)

    def set_voice_mode(self, chat_id: int, voice_mode: str) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "UPDATE users SET voice_mode = ? WHERE chat_id = ?",
                (voice_mode, chat_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"DB error in set_voice_mode: {type(e).__name__}: {e}")
        finally:
            if conn:
                conn.close()

    def set_lang(self, chat_id: int, lang: str) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "UPDATE users SET lang = ? WHERE chat_id = ?",
                (lang, chat_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"DB error in set_lang: {type(e).__name__}: {e}")
        finally:
            if conn:
                conn.close()

    def get_or_create_user(self, chat_id: int, username: str) -> User:
        user = self.get_user(chat_id)
        if not user:
            user = self.create_user(chat_id, username)
        return user
