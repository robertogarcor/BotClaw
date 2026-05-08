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