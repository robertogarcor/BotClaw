import pytest
from datetime import datetime


class TestUser:
    def test_user_creation(self):
        from bot.models.user import User
        user = User(chat_id=12345, username="testuser")
        assert user.chat_id == 12345
        assert user.username == "testuser"
        assert user.voice_mode == "off"
        assert user.created_at is not None

    def test_user_default_values(self):
        from bot.models.user import User
        user = User(chat_id=12345)
        assert user.username == ""
        assert user.voice_mode == "off"


class TestSession:
    def test_session_creation(self):
        from bot.models.session import Session
        session = Session(chat_id=12345)
        assert session.chat_id == 12345
        assert session.session_id == ""
        assert session.created_at is not None

    def test_session_is_active_false_when_empty(self):
        from bot.models.session import Session
        session = Session(chat_id=12345)
        assert session.is_active() is False

    def test_session_is_active_true_when_set(self):
        from bot.models.session import Session
        session = Session(chat_id=12345, session_id="ses_abc123")
        assert session.is_active() is True