import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch, ANY


def _run_async(coro):
    return asyncio.run(coro)


class TestProjectsCommand:
    @pytest.fixture(autouse=True)
    def setup_settings(self, mock_settings):
        mock_settings.PROJECTS_BASE_DIR = "/home/test/Projects"
        return mock_settings

    def _make_projects_response(self, projects):
        resp = Mock(status_code=200)
        resp.json.return_value = projects
        return resp

    def _make_sessions_response(self, sessions):
        resp = Mock(status_code=200)
        resp.json.return_value = sessions
        return resp

    def _make_update(self):
        chat = MagicMock()
        chat.id = 12345
        user = MagicMock()
        user.username = "testuser"
        message = MagicMock()
        message.chat = chat
        message.from_user = user
        message.reply_text = AsyncMock()
        update = MagicMock()
        update.effective_chat = chat
        update.effective_user = user
        update.message = message
        return update

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_no_projects_found(self, mock_get_sessions, mock_create_server, setup_settings):
        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response([]),
            self._make_sessions_response([]),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "No projects found" in sent_text
        assert "/home/test/Projects" in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_lists_projects_with_sessions(self, mock_get_sessions, mock_create_server, setup_settings):
        projects = [
            {"id": "uuid-1", "worktree": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
            {"id": "uuid-2", "worktree": "/home/test/Projects/Beta", "time": {"created": 1700002000000, "updated": 1700003000000}},
        ]
        sessions = [
            {"id": "ses_alpha", "projectID": "uuid-1", "directory": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
            {"id": "ses_beta", "projectID": "uuid-2", "directory": "/home/test/Projects/Beta", "time": {"created": 1700002000000, "updated": 1700003000000}},
        ]

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "Alpha" in sent_text
        assert "Beta" in sent_text
        assert "ses_alpha" in sent_text
        assert "ses_beta" in sent_text
        assert "/home/test/Projects/Alpha" in sent_text
        assert "/home/test/Projects/Beta" in sent_text
        assert "✅" not in sent_text
        assert "➡️" in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_includes_global_id_projects(self, mock_get_sessions, mock_create_server, setup_settings):
        projects = [
            {"id": "global", "worktree": "/home/test/Projects/FromCreate", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]
        sessions = [
            {"id": "ses_create", "projectID": "global", "directory": "/home/test/Projects/FromCreate", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "FromCreate" in sent_text
        assert "ses_create" in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_filters_outside_base_dir(self, mock_get_sessions, mock_create_server, setup_settings):
        projects = [
            {"id": "uuid-1", "worktree": "/home/test/Projects/Inside", "time": {"created": 1700000000000, "updated": 1700001000000}},
            {"id": "uuid-2", "worktree": "/somewhere/else/Outside", "time": {"created": 1700002000000, "updated": 1700003000000}},
        ]
        sessions = []

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "Inside" in sent_text
        assert "Outside" not in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    @patch("bot.handlers.command_project.Path.exists")
    def test_orphan_global_session_directory_exists(self, mock_exists, mock_get_sessions, mock_create_server, setup_settings):
        mock_exists.return_value = True

        projects = []
        sessions = [
            {"id": "ses_orphan", "projectID": "global", "directory": "/home/test/Projects/OrphanDir", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "OrphanDir" in sent_text
        assert "ses_orphan" in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    @patch("bot.handlers.command_project.Path.exists")
    def test_orphan_global_session_directory_missing(self, mock_exists, mock_get_sessions, mock_create_server, setup_settings):
        mock_exists.return_value = False

        projects = []
        sessions = [
            {"id": "ses_ghost", "projectID": "global", "directory": "/home/test/Projects/GhostDir", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "No projects found" in sent_text
        assert "GhostDir" not in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    @patch("bot.handlers.command_project.Path.exists")
    def test_excludes_base_dir_itself(self, mock_exists, mock_get_sessions, mock_create_server, setup_settings):
        mock_exists.return_value = True

        projects = []
        sessions = [
            {"id": "ses_base", "projectID": "global", "directory": "/home/test/Projects", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "No projects found" in sent_text
        assert "Projects" not in sent_text or "Projects" in sent_text and "ses_base" not in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_session_matched_by_directory(self, mock_get_sessions, mock_create_server, setup_settings):
        projects = [
            {"id": "uuid-1", "worktree": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]
        sessions = [
            {"id": "ses_alpha_1", "projectID": "uuid-1", "directory": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
            {"id": "ses_alpha_2", "projectID": "uuid-1", "directory": "/home/test/Projects/Alpha", "time": {"created": 1700002000000, "updated": 1700003000000}},
            {"id": "ses_other", "projectID": "uuid-2", "directory": "/home/test/Projects/Beta", "time": {"created": 1700004000000, "updated": 1700005000000}},
        ]

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "Alpha" in sent_text
        assert "ses_alpha_1" in sent_text
        assert "ses_alpha_2" in sent_text
        assert "➡️" in sent_text
        assert "✅" not in sent_text
        assert "ses_other" not in sent_text

        alpha_1_pos = sent_text.index("ses_alpha_1")
        alpha_2_pos = sent_text.index("ses_alpha_2")
        assert alpha_2_pos < alpha_1_pos, "most recent session should appear first"
        arrow_pos = sent_text.index("➡️")
        assert alpha_2_pos < arrow_pos < alpha_2_pos + 50, "arrow should be near ses_alpha_2"

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_api_failure_shows_error(self, mock_get_sessions, mock_create_server, setup_settings):
        mock_server = MagicMock()
        mock_response = Mock(status_code=500, text="Internal Server Error")
        mock_server._session.get.return_value = mock_response
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "Failed to fetch projects" in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_no_projects_within_base_dir(self, mock_get_sessions, mock_create_server, setup_settings):
        projects = [
            {"id": "uuid-1", "worktree": "/other/path/Project", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]
        sessions = []

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = []

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "No projects found" in sent_text
        assert "/other/path/Project" not in sent_text

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_session")
    @patch("bot.handlers.command_project.SessionManager.get_current_path")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_marks_active_project_session_with_check(self, mock_get_sessions, mock_get_path, mock_get_session, mock_create_server, setup_settings):
        projects = [
            {"id": "uuid-1", "worktree": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
            {"id": "uuid-2", "worktree": "/home/test/Projects/Beta", "time": {"created": 1700002000000, "updated": 1700003000000}},
        ]
        sessions = [
            {"id": "ses_alpha_1", "projectID": "uuid-1", "directory": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
            {"id": "ses_alpha_2", "projectID": "uuid-1", "directory": "/home/test/Projects/Alpha", "time": {"created": 1700002000000, "updated": 1700003000000}},
            {"id": "ses_beta", "projectID": "uuid-2", "directory": "/home/test/Projects/Beta", "time": {"created": 1700004000000, "updated": 1700005000000}},
        ]

        active_session_mock = MagicMock()
        active_session_mock.session_id = "ses_alpha_1"
        mock_get_path.return_value = "/home/test/Projects/Alpha"
        mock_get_session.return_value = active_session_mock
        mock_get_sessions.return_value = []

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(sessions),
        ]
        mock_create_server.return_value = mock_server

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "✅" in sent_text
        assert "➡️" in sent_text
        alpha_1_pos = sent_text.index("ses_alpha_1")
        check_pos = sent_text.index("✅")
        assert abs(check_pos - alpha_1_pos) < 50, "check should be near ses_alpha_1"
        alpha_2_pos = sent_text.index("ses_alpha_2")
        arrow_pos = sent_text.index("➡️")
        assert abs(arrow_pos - alpha_2_pos) < 50, "arrow should be near ses_alpha_2 (most recent of Alpha)"

    @patch("bot.handlers.command_project.ServerFactory.create_opencode")
    @patch("bot.handlers.command_project.SessionManager.get_sessions_from_api")
    def test_fallback_to_get_sessions_from_api(self, mock_get_sessions, mock_create_server, setup_settings):
        projects = [
            {"id": "uuid-1", "worktree": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
        ]
        batch_sessions = []
        api_sessions = [
            {"id": "ses_fallback_1", "directory": "/home/test/Projects/Alpha", "time": {"created": 1700000000000, "updated": 1700001000000}},
            {"id": "ses_fallback_2", "directory": "/home/test/Projects/Alpha", "time": {"created": 1700002000000, "updated": 1700003000000}},
        ]

        mock_server = MagicMock()
        mock_server._session.get.side_effect = [
            self._make_projects_response(projects),
            self._make_sessions_response(batch_sessions),
        ]
        mock_create_server.return_value = mock_server
        mock_get_sessions.return_value = api_sessions

        from bot.handlers.command_project import projects_command

        update = self._make_update()
        context = MagicMock()
        _run_async(projects_command(update, context))

        sent_text = update.message.reply_text.call_args[0][0]
        assert "Alpha" in sent_text
        assert "ses_fallback_1" in sent_text
        assert "ses_fallback_2" in sent_text
        assert "➡️" in sent_text
        assert "✅" not in sent_text
        assert "Created:" in sent_text
        assert "Last access:" in sent_text
