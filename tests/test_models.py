import pytest
from datetime import datetime


class TestUser:
    def test_user_creation(self):
        from bot.models.user import User
        user = User(chat_id=12345, username="testuser")
        assert user.chat_id == 12345
        assert user.username == "testuser"
        assert user.working_dir == ""
        assert user.created_at is not None

    def test_user_has_project_false_when_empty(self):
        from bot.models.user import User
        user = User(chat_id=12345, username="testuser")
        assert user.has_project() is False

    def test_user_has_project_true_when_set(self):
        from bot.models.user import User
        user = User(chat_id=12345, username="testuser", working_dir="/home/user/project")
        assert user.has_project() is True


class TestSession:
    def test_session_creation(self):
        from bot.models.session import Session
        session = Session(chat_id=12345)
        assert session.chat_id == 12345
        assert session.session_id == ""
        assert session.working_dir == ""
        assert session.created_at is not None

    def test_session_is_active_false_when_empty(self):
        from bot.models.session import Session
        session = Session(chat_id=12345)
        assert session.is_active() is False

    def test_session_is_active_true_when_set(self):
        from bot.models.session import Session
        session = Session(chat_id=12345, session_id="ses_abc123")
        assert session.is_active() is True