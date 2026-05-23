import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


def _run_async(coro):
    return asyncio.run(coro)


class TestUseCommand:
    @pytest.fixture(autouse=True)
    def setup_settings(self, mock_settings):
        return mock_settings

    def _make_server(self, session_details):
        mock_server = MagicMock()
        mock_server.get_session_details.return_value = session_details
        return mock_server

    def _make_update(self):
        chat = MagicMock()
        chat.id = 12345
        message = MagicMock()
        message.chat = chat
        message.reply_text = AsyncMock()
        update = MagicMock()
        update.effective_chat = chat
        update.message = message
        return update

    @patch("bot.handlers.command_sessions.ServerFactory.create_opencode")
    @patch("bot.handlers.command_sessions.SessionManager.set_session_id")
    @patch("bot.handlers.command_sessions.SessionManager.get_current_path")
    def test_use_session_belongs_to_active_project(self, mock_get_path, mock_set_sid, mock_create_server, setup_settings):
        mock_get_path.return_value = "/home/test/Projects/Alpha"
        mock_create_server.return_value = self._make_server(
            {"id": "ses_1", "directory": "/home/test/Projects/Alpha", "title": "Test"}
        )

        from bot.handlers.command_sessions import use_command

        update = self._make_update()
        context = MagicMock()
        context.args = ["ses_1"]
        _run_async(use_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "✅" in sent_text
        mock_set_sid.assert_called_once()

    @patch("bot.handlers.command_sessions.ServerFactory.create_opencode")
    @patch("bot.handlers.command_sessions.SessionManager.set_session_id")
    @patch("bot.handlers.command_sessions.SessionManager.get_current_path")
    def test_use_session_from_different_project(self, mock_get_path, mock_set_sid, mock_create_server, setup_settings):
        mock_get_path.return_value = "/home/test/Projects/Alpha"
        mock_create_server.return_value = self._make_server(
            {"id": "ses_2", "directory": "/home/test/Projects/Beta", "title": "Other"}
        )

        from bot.handlers.command_sessions import use_command

        update = self._make_update()
        context = MagicMock()
        context.args = ["ses_2"]
        _run_async(use_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "⚠️" in sent_text
        mock_set_sid.assert_not_called()
