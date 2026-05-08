import json
import logging
import time
from typing import Optional
import requests

from bot.servers.base import BaseServer, ServerResponse, ControlRequest

logger = logging.getLogger(__name__)


class OpenCodeServer(BaseServer):
    def __init__(self, url: str, password: str = ""):
        self.url = url.rstrip("/")
        self.password = password
        self.auth = ("opencode", password) if password else None
        self._session = requests.Session()
        if self.auth:
            self._session.auth = self.auth

    def connect(self) -> bool:
        try:
            response = self._session.get(f"{self.url}/doc", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def disconnect(self) -> bool:
        self._session.close()
        return True

    def create_session(self, working_dir: str) -> str:
        logger.info(f"Creating session with working_dir: {working_dir}")

        try:
            response = self._session.post(
                f"{self.url}/session",
                json={"title": f"BotClaw session for {working_dir}"},
                timeout=30
            )
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return ""

        logger.info(f"Session endpoint status: {response.status_code}")
        logger.info(f"Session endpoint response: {response.text[:1000] if response.text else 'empty'}")

        if response.status_code == 204:
            logger.info("No content - using default session")
            return "default"

        if not response.text:
            logger.warning("Empty response, using default session")
            return "default"

        try:
            data = response.json()
            logger.info(f"Parsed JSON: {data}")

            if "id" in data:
                return data.get("id", "")
            else:
                logger.warning(f"Unexpected response format: {data}")
                return "default"

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, response: {response.text}")
            return "default"

    def send_prompt(self, session_id: str, prompt: str) -> ServerResponse:
        logger.info(f"Sending prompt to session: {session_id}")

        try:
            submit_response = self._session.post(
                f"{self.url}/session/{session_id}/message",
                json={"parts": [{"type": "text", "text": prompt}]},
                timeout=30
            )
        except requests.Timeout:
            logger.error("Timeout sending prompt to OpenCode server")
            raise Exception("Timeout connecting to OpenCode server. Is it running?")
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise Exception(f"Cannot connect to OpenCode server: {e}")

        logger.info(f"Submit prompt status: {submit_response.status_code}")
        logger.info(f"Submit prompt response: {submit_response.text[:1000] if submit_response.text else 'empty'}")

        try:
            submit_response.raise_for_status()
        except requests.HTTPError as e:
            logger.error(f"HTTP Error sending prompt: {e}, response: {submit_response.text}")
            raise

        try:
            response_data = submit_response.json()
            logger.info(f"Response data: {response_data}")

            if "parts" in response_data:
                parts = response_data.get("parts", [])
                text_parts = []
                for part in parts:
                    if part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    elif part.get("type") == "tool-result":
                        text_parts.append(f"[Tool: {part.get('tool', 'unknown')}]")

                if text_parts:
                    return ServerResponse(content="\n".join(text_parts))

            return ServerResponse(content="Response received")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return ServerResponse(content=f"Error parsing response: {e}")

    def continue_session(self, session_id: str) -> bool:
        response = self._session.get(
            f"{self.url}/session/{session_id}",
            timeout=30
        )
        return response.status_code == 200

    def execute_command(self, session_id: str, command: str) -> bool:
        response = self._session.post(
            f"{self.url}/tui/execute-command",
            json={"command": command, "session": session_id},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("success", False)

    def send_control_response(self, session_id: str, response: str) -> ServerResponse:
        control_response = self._session.post(
            f"{self.url}/tui/control/response",
            json={"body": response, "session": session_id},
            timeout=30
        )
        control_response.raise_for_status()
        return self._wait_for_response(session_id)

    def _wait_for_response(self, session_id: str, timeout: int = 120) -> ServerResponse:
        max_attempts = timeout
        for _ in range(max_attempts):
            time.sleep(1)
            response = self._session.get(
                f"{self.url}/tui/control/next",
                params={"session": session_id},
                timeout=30
            )
            if response.status_code == 204:
                continue

            data = response.json()
            if data.get("waiting"):
                continue

            content = data.get("response", {})
            if content.get("output"):
                text = content.get("output", "")
                return ServerResponse(content=text)

            if content.get("control_request"):
                req = content.get("control_request", {})
                ctrl_req = ControlRequest(
                    request_id=req.get("id", ""),
                    question=req.get("prompt", ""),
                    options=req.get("options", [])
                )
                return ServerResponse(
                    content=content.get("message", "Waiting for input..."),
                    control_request=ctrl_req
                )

        return ServerResponse(content="Timeout: No response received")

    def list_sessions(self) -> list:
        try:
            response = self._session.get(
                f"{self.url}/session",
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException as e:
            logger.error(f"Error listing sessions: {e}")
            return []

    def get_session_details(self, session_id: str) -> dict:
        try:
            response = self._session.get(
                f"{self.url}/session/{session_id}",
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException as e:
            logger.error(f"Error getting session details: {e}")
            return {}

    def list_mcp_servers(self) -> dict:
        try:
            response = self._session.get(
                f"{self.url}/mcp",
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException as e:
            logger.error(f"Error listing MCP servers: {e}")
            return {}