import pytest
from unittest.mock import patch, MagicMock, Mock
import requests


class TestOpenCodeServerExtended:
    @patch('requests.Session')
    def test_list_agents_returns_list(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = [
            {"name": "build", "mode": "primary"},
            {"name": "explore", "mode": "subagent"}
        ]
        mock_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        agents = server.list_agents()
        assert isinstance(agents, list)
        assert len(agents) == 2
        assert agents[0]["name"] == "build"

    @patch('requests.Session')
    def test_list_agents_returns_empty_on_error(self, mock_session_class):
        mock_instance = MagicMock()
        mock_instance.get.side_effect = requests.RequestException()
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        agents = server.list_agents()
        assert isinstance(agents, list)
        assert len(agents) == 0

    @patch('requests.Session')
    def test_rename_session_success(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200)
        mock_instance.patch.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        result = server.rename_session("ses_123", "New Title")
        assert result is True

    @patch('requests.Session')
    def test_rename_session_failure(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=404, text="Not found")
        mock_instance.patch.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        result = server.rename_session("ses_123", "New Title")
        assert result is False

    @patch('requests.Session')
    def test_send_prompt_with_agent(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200, text='{"parts":[{"type":"text","text":"ok"}]}')
        mock_response.json.return_value = {"parts": [{"type": "text", "text": "ok"}]}
        mock_instance.post.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        result = server.send_prompt("ses_123", "hello", agent="build")
        assert "ok" in result.content
        _, kwargs = mock_instance.post.call_args
        assert kwargs["json"]["agent"] == "build"

    @patch('requests.Session')
    def test_send_prompt_without_agent(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200, text='{"parts":[{"type":"text","text":"ok"}]}')
        mock_response.json.return_value = {"parts": [{"type": "text", "text": "ok"}]}
        mock_instance.post.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        result = server.send_prompt("ses_123", "hello")
        assert "ok" in result.content
        _, kwargs = mock_instance.post.call_args
        assert "agent" not in kwargs["json"]

    @patch('requests.Session')
    def test_get_session_messages_returns_list(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = [
            {"id": "msg_1", "info": {"mode": "build"}},
            {"id": "msg_2", "info": {"mode": "plan"}},
        ]
        mock_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        messages = server.get_session_messages("ses_123")
        assert isinstance(messages, list)
        assert len(messages) == 2

    @patch('requests.Session')
    def test_get_session_messages_returns_empty_on_error(self, mock_session_class):
        mock_instance = MagicMock()
        mock_instance.get.side_effect = requests.RequestException()
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        messages = server.get_session_messages("ses_123")
        assert isinstance(messages, list)
        assert len(messages) == 0

    @patch('requests.Session')
    def test_list_agents_handles_agents_format(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"agents": [{"name": "build", "mode": "primary"}]}
        mock_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        agents = server.list_agents()
        assert isinstance(agents, list)
        assert len(agents) == 1

    @patch('requests.Session')
    def test_list_agents_handles_items_format(self, mock_session_class):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"items": [{"name": "explore", "mode": "subagent"}]}
        mock_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        agents = server.list_agents()
        assert isinstance(agents, list)
        assert len(agents) == 1
