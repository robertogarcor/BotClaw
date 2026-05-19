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
