import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / "config" / ".env")


class Settings:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    OPENCODE_SERVER_URL = os.getenv("OPENCODE_SERVER_URL", "http://localhost:4096")
    OPENCODE_SERVER_PASSWORD = os.getenv("OPENCODE_SERVER_PASSWORD", "")
    USERS_ALLOWED = [u.strip().lstrip("@") for u in os.getenv("USERS_ALLOWED", "").split(",") if u.strip()] if os.getenv("USERS_ALLOWED") else []
    USER_IDS_ALLOWED = [u.strip() for u in os.getenv("USER_IDS_ALLOWED", "").split(",") if u.strip()] if os.getenv("USER_IDS_ALLOWED") else []
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TTS_VOICE = os.getenv("TTS_VOICE", "es-MX-DaliaNeural")
    PROJECTS_BASE_DIR = os.getenv("PROJECTS_BASE_DIR", str(Path.home() / "projects"))
    DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")

    DATA_DIR = BASE_DIR / "data"
    DATABASE_PATH = DATA_DIR / "botclaw.db"

    @classmethod
    def validate(cls) -> bool:
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        return True

    @classmethod
    def is_user_allowed(cls, username: str = None, user_id: int = None) -> bool:
        if not cls.USERS_ALLOWED and not cls.USER_IDS_ALLOWED:
            return True

        if username and username.lstrip("@") in cls.USERS_ALLOWED:
            return True

        if user_id and str(user_id) in cls.USER_IDS_ALLOWED:
            return True

        return False