from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    chat_id: int
    session_id: str = ""
    working_dir: str = ""
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def is_active(self) -> bool:
        return bool(self.session_id)