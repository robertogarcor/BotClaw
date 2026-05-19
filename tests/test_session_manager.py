import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestSessionManager:
    def test_create_project_creates_directory(self, session_manager, tmp_path):
        new_path = str(tmp_path / "new_project")
        with patch.object(session_manager, 'init_project', return_value=("ses_123", True, {})):
            session_id, is_new, _ = session_manager.create_project(0, new_path)
        assert Path(new_path).exists()
        assert Path(new_path).is_dir()

    def test_create_project_runs_git_init(self, session_manager, tmp_path):
        new_path = str(tmp_path / "git_project")
        with patch.object(session_manager, 'init_project', return_value=("ses_123", True, {})):
            session_manager.create_project(0, new_path)
        assert (Path(new_path) / ".git").exists()

    def test_create_project_creates_templates(self, session_manager, tmp_path):
        new_path = str(tmp_path / "template_project")
        with patch.object(session_manager, 'init_project', return_value=("ses_123", True, {})):
            session_manager.create_project(0, new_path)
        assert (Path(new_path) / "AGENTS.md").exists()
        assert (Path(new_path) / "PRODUCT.md").exists()
        assert (Path(new_path) / "ARCHITECTURE.md").exists()
        assert (Path(new_path) / "SPEC.md").exists()
        assert (Path(new_path) / "HISTORY.md").exists()

    def test_create_project_skips_existing_templates(self, session_manager, tmp_path):
        new_path = str(tmp_path / "existing_project")
        Path(new_path).mkdir()
        (Path(new_path) / "AGENTS.md").write_text("# Custom content")
        original_content = "# Custom content"
        with patch.object(session_manager, 'init_project', return_value=("ses_123", True, {})):
            session_manager.create_project(0, new_path)
        assert (Path(new_path) / "AGENTS.md").read_text() == original_content

    def test_create_project_calls_init_project(self, session_manager, tmp_path):
        new_path = str(tmp_path / "init_test_project")
        with patch.object(session_manager, 'init_project', return_value=("ses_456", True, {"id": "ses_456"})) as mock_init:
            session_manager.create_project(0, new_path)
            mock_init.assert_called_once_with(0, new_path)

    def test_init_project_reuses_existing_session(self, session_manager):
        with patch.object(session_manager, 'get_sessions_from_api', return_value=[
            {"id": "ses_existing", "time": {"created": 1000, "updated": 2000}}
        ]):
            session_id, is_new, data = session_manager.init_project(123, "/some/path")
        assert session_id == "ses_existing"
        assert is_new is False

    def test_init_project_creates_new_session(self, session_manager):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "ses_new"}
        with patch.object(session_manager, 'get_sessions_from_api', return_value=[]), \
             patch.object(session_manager, '_get_server') as mock_get_server:
            mock_server = MagicMock()
            mock_server._session = MagicMock()
            mock_server._session.post.return_value = mock_response
            mock_get_server.return_value = mock_server
            session_id, is_new, data = session_manager.init_project(123, "/new/path")
        assert is_new is True

    def test_save_session_insert_and_update(self, session_manager):
        session_manager.save_session(123, "/path/one", "ses_1", "2026-01-01", "2026-01-02")
        session = session_manager.get_session(123, "/path/one")
        assert session is not None
        assert session.session_id == "ses_1"
        session_manager.save_session(123, "/path/one", "ses_2", "2026-01-01", "2026-01-03")
        session = session_manager.get_session(123, "/path/one")
        assert session.session_id == "ses_2"

    def test_set_active_path(self, session_manager):
        session_manager.save_session(123, "/path/a", "ses_a")
        session_manager.save_session(123, "/path/b", "ses_b")
        session_manager.set_active_path(123, "/path/a")
        assert session_manager.get_current_path(123) == "/path/a"
        session_manager.set_active_path(123, "/path/b")
        assert session_manager.get_current_path(123) == "/path/b"

    def test_get_current_path_returns_active(self, session_manager):
        assert session_manager.get_current_path(999) is None
        session_manager.save_session(999, "/active/path", "ses_active")
        session_manager.set_active_path(999, "/active/path")
        assert session_manager.get_current_path(999) == "/active/path"

    def test_sync_session_dates_from_api(self, session_manager):
        session_manager.save_session(123, "/sync/path", "ses_sync")
        mock_server = MagicMock()
        mock_server.get_session_details.return_value = {
            "time": {"created": 1700000000000, "updated": 1700001000000}
        }
        with patch.object(session_manager, '_get_server', return_value=mock_server):
            session_manager.sync_session_dates_from_api(123, "/sync/path")
        session = session_manager.get_session(123, "/sync/path")
        assert session is not None
        assert "2023" in str(session.created_at)
