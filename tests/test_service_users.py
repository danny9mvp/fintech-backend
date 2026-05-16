from datetime import datetime
from unittest.mock import MagicMock, patch

from app.service.user_service import UserService
from app.schemas.user import UserResponse


class TestUserServiceUpdate:
    def test_returns_user_response(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_updated = MagicMock()
        mock_updated.id = 1
        mock_updated.email = "alice@example.com"
        mock_updated.username = "alice_updated"
        mock_updated.created_at = datetime.now()
        body = MagicMock()
        body.model_dump.return_value = {"username": "alice_updated"}

        with patch("app.service.user_service.user_crud") as crud:
            crud.update.return_value = mock_updated
            result = UserService(db, user).update(body)

        assert isinstance(result, UserResponse)
        assert result.username == "alice_updated"
        assert result.email == "alice@example.com"
        assert result.id == 1
        crud.update.assert_called_once_with(db, user, username="alice_updated")

    def test_updates_password(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_updated = MagicMock()
        mock_updated.id = 1
        mock_updated.email = "alice@example.com"
        mock_updated.username = "alice"
        mock_updated.created_at = datetime.now()
        body = MagicMock()
        body.model_dump.return_value = {"password": "new_secret"}

        with patch("app.service.user_service.user_crud") as crud:
            crud.update.return_value = mock_updated
            result = UserService(db, user).update(body)

        assert isinstance(result, UserResponse)
        crud.update.assert_called_once_with(db, user, password="new_secret")
