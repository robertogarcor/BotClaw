import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token_123',
        'OPENCODE_SERVER_URL': 'http://localhost:4096',
        'OPENCODE_SERVER_PASSWORD': '',
        'USERS_ALLOWED': '',
        'USER_IDS_ALLOWED': '',
        'LOG_LEVEL': 'DEBUG'
    }):
        yield


@pytest.fixture
def mock_settings(mock_env):
    from bot.config import settings as settings_module
    settings_module.load_dotenv = MagicMock()
    from importlib import reload
    reload(settings_module)
    return settings_module.Settings


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test_bot.db"
    return str(db_path)


@pytest.fixture
def session_manager(temp_db):
    from bot.services.session_manager import SessionManager
    from bot.config import settings as settings_module
    original_path = settings_module.Settings.DATABASE_PATH
    settings_module.Settings.DATABASE_PATH = temp_db
    sm = SessionManager()
    yield sm
    settings_module.Settings.DATABASE_PATH = original_path


@pytest.fixture
def user_manager(temp_db):
    from bot.services.user_manager import UserManager
    from bot.config import settings as settings_module
    original_path = settings_module.Settings.DATABASE_PATH
    settings_module.Settings.DATABASE_PATH = temp_db
    um = UserManager()
    yield um
    settings_module.Settings.DATABASE_PATH = original_path


@pytest.fixture
def mock_server():
    from bot.servers.opencode import OpenCodeServer
    with patch('requests.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        server = OpenCodeServer(url="http://localhost:4096", password="")
        server._session = mock_session
        yield server