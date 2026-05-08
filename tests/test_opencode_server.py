import pytest
from unittest.mock import patch, MagicMock, Mock
import requests


class TestOpenCodeServer:
    def test_opencode_server_creation(self):
        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096", password="test")
        assert server.url == "http://localhost:4096"
        assert server.password == "test"
        assert server.auth == ("opencode", "test")

    def test_opencode_server_without_password(self):
        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096", password="")
        assert server.auth is None

    @patch('requests.Session')
    def test_connect_returns_true_when_server_reachable(self, mock_session):
        mock_instance = MagicMock()
        mock_instance.get.return_value = Mock(status_code=200)
        mock_session.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        result = server.connect()
        assert result is True

    @patch('requests.Session')
    def test_connect_returns_false_when_server_unreachable(self, mock_session):
        mock_instance = MagicMock()
        mock_instance.get.side_effect = requests.RequestException()
        mock_session.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        result = server.connect()
        assert result is False

    def test_disconnect_closes_session(self):
        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        assert server.disconnect() is True

    @patch('requests.Session')
    def test_list_sessions_returns_list(self, mock_session):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = [{"id": "ses_1", "title": "Test"}]
        mock_instance.get.return_value = mock_response
        mock_session.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        sessions = server.list_sessions()
        assert isinstance(sessions, list)

    @patch('requests.Session')
    def test_list_mcp_servers_returns_dict(self, mock_session):
        mock_instance = MagicMock()
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"git": {"connected": True}}
        mock_instance.get.return_value = mock_response
        mock_session.return_value = mock_instance

        from bot.servers.opencode import OpenCodeServer
        server = OpenCodeServer(url="http://localhost:4096")
        mcp = server.list_mcp_servers()
        assert isinstance(mcp, dict)