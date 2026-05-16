from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi import status


def _override_current_user(client, user_id=1):
    from app.api.deps import get_current_user
    from app.model.user import User

    client.app.dependency_overrides[get_current_user] = lambda: User(
        id=user_id,
        email="test@example.com",
        username="testuser",
        pwd_hash="xxx",
        firstname="Test",
        lastname="User",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        last_updated_at=datetime.now(timezone.utc),
        last_login_at=None,
    )


def test_get_me(client):
    _override_current_user(client)

    resp = client.get("/users/me")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["firstname"] == "Test"
    assert data["lastname"] == "User"
    assert "id" in data
    assert "created_at" not in data
    assert "is_active" not in data
    assert "last_updated_at" not in data
    assert "last_login_at" not in data


def test_get_me_unauthorized(client):
    resp = client.get("/users/me")
    assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


def _make_mock_user(id=1, email="test@example.com", username="testuser", pwd_hash="xxx"):
    u = MagicMock()
    u.id = id
    u.email = email
    u.username = username
    u.pwd_hash = pwd_hash
    u.firstname = "Test"
    u.lastname = "User"
    u.middlename = None
    u.second_lastname = None
    u.is_active = True
    u.last_updated_at = datetime.now(timezone.utc)
    u.last_login_at = None
    return u


def test_update_me_username(client):
    _override_current_user(client)

    mock_updated = _make_mock_user(username="newname")

    with patch("app.crud.user.user_crud.update", return_value=mock_updated):
        resp = client.patch("/users/me", json={"username": "newname"})

    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_email(client):
    _override_current_user(client)

    mock_updated = _make_mock_user(email="new@example.com")

    with patch("app.crud.user.user_crud.update", return_value=mock_updated):
        resp = client.patch("/users/me", json={"email": "new@example.com"})

    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_password(client):
    _override_current_user(client)

    mock_updated = _make_mock_user()

    with patch("app.crud.user.user_crud.update", return_value=mock_updated):
        resp = client.patch("/users/me", json={"password": "newpassword123"})

    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_all_fields(client):
    _override_current_user(client)

    mock_updated = _make_mock_user(
        username="newname", email="new@example.com"
    )

    with patch("app.crud.user.user_crud.update", return_value=mock_updated):
        resp = client.patch(
            "/users/me",
            json={
                "username": "newname",
                "email": "new@example.com",
                "password": "newpassword123",
            },
        )

    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_no_fields(client):
    _override_current_user(client)

    with patch("app.crud.user.user_crud.update", return_value=_make_mock_user()):
        resp = client.patch("/users/me", json={})

    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_unauthorized(client):
    resp = client.patch("/users/me", json={"username": "hacker"})
    assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
