from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    chat_id: int
    username: str = ""
    voice_mode: str = "off"
    lang: str = "en"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
