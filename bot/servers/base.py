from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ControlRequest:
    request_id: str
    question: str
    options: list[str]


@dataclass
class ServerResponse:
    content: str
    control_request: Optional[ControlRequest] = None


class BaseServer(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def create_session(self, working_dir: str) -> str:
        pass

    @abstractmethod
    def send_prompt(self, session_id: str, prompt: str) -> ServerResponse:
        pass

    @abstractmethod
    def continue_session(self, session_id: str) -> bool:
        pass

    @abstractmethod
    def execute_command(self, session_id: str, command: str) -> bool:
        pass

    @abstractmethod
    def send_control_response(self, session_id: str, response: str) -> ServerResponse:
        pass

    @abstractmethod
    def list_sessions(self) -> list:
        pass

    @abstractmethod
    def get_session_details(self, session_id: str) -> dict:
        pass

    @abstractmethod
    def list_mcp_servers(self) -> dict:
        pass