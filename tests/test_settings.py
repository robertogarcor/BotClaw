import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestSettings:
    def test_settings_class_has_required_attrs(self):
        from bot.config.settings import Settings
        assert hasattr(Settings, 'TELEGRAM_BOT_TOKEN')
        assert hasattr(Settings, 'OPENCODE_SERVER_URL')
        assert hasattr(Settings, 'USERS_ALLOWED')
        assert hasattr(Settings, 'USER_IDS_ALLOWED')

    def test_validate_raises_without_token(self):
        from bot.config.settings import Settings
        original_token = Settings.TELEGRAM_BOT_TOKEN
        Settings.TELEGRAM_BOT_TOKEN = ""
        with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
            Settings.validate()
        Settings.TELEGRAM_BOT_TOKEN = original_token

    def test_is_user_allowed_allows_all_when_empty(self):
        from bot.config.settings import Settings
        original_users = Settings.USERS_ALLOWED
        original_ids = Settings.USER_IDS_ALLOWED
        Settings.USERS_ALLOWED = []
        Settings.USER_IDS_ALLOWED = []
        assert Settings.is_user_allowed("any_user", 999) is True
        Settings.USERS_ALLOWED = original_users
        Settings.USER_IDS_ALLOWED = original_ids

    def test_is_user_allowed_blocks_unauthorized(self):
        from bot.config.settings import Settings
        original_users = Settings.USERS_ALLOWED
        original_ids = Settings.USER_IDS_ALLOWED
        Settings.USERS_ALLOWED = ['user1']
        Settings.USER_IDS_ALLOWED = ['123']
        assert Settings.is_user_allowed("user2", 456) is False
        assert Settings.is_user_allowed("user1", 456) is True
        assert Settings.is_user_allowed("user2", 123) is True
        Settings.USERS_ALLOWED = original_users
        Settings.USER_IDS_ALLOWED = original_ids