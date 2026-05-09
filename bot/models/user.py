from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    chat_id: int
    username: str
    working_dir: str = ""
    voice_mode: str = "off"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def has_project(self) -> bool:
        return bool(self.working_dir)