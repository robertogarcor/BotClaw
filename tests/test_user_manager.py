import pytest


class TestUserManager:
    def test_get_or_create_user_creates_new(self, user_manager):
        user = user_manager.get_or_create_user(12345, "testuser")
        assert user is not None
        assert user.chat_id == 12345
        assert user.username == "testuser"
        assert user.voice_mode == "off"

    def test_get_or_create_user_returns_existing(self, user_manager):
        user_manager.get_or_create_user(12345, "testuser")
        user = user_manager.get_or_create_user(12345, "updated_user")
        assert user.chat_id == 12345
        assert user.username == "testuser"

    def test_get_user_returns_none(self, user_manager):
        user = user_manager.get_user(99999)
        assert user is None
