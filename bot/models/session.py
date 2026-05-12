from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    chat_id: int
    path: str = ""
    session_id: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    last_access: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def is_active(self) -> bool:
        return bool(self.session_id)
