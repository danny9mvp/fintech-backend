from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from fastapi import status


def _make_mock_user(id=1, email="test@test.com", username="test", pwd_hash="hashed"):
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
    u.last_updated_at = datetime.now()
    u.last_login_at = None
    return u


def _make_mock_refresh_token(
    user_id=1, token_hash="abc", revoked_at=None, expires_at=None
):
    t = MagicMock()
    t.id = 1
    t.user_id = user_id
    t.token_hash = token_hash
    t.expires_at = expires_at or (datetime.now(timezone.utc) + timedelta(days=30))
    t.revoked_at = revoked_at
    return t


def test_register(client):
    mock_user = _make_mock_user()

    with patch("app.crud.user.user_crud.get_by_email", return_value=None), \
         patch("app.crud.user.user_crud.create", return_value=mock_user):
        resp = client.post(
            "/auth/register",
            json={
                "email": "alice@example.com",
                "password": "strong123",
                "username": "alice",
            },
        )

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    mock_user = _make_mock_user(email="dup@example.com")

    with patch("app.crud.user.user_crud.get_by_email", return_value=mock_user):
        resp = client.post(
            "/auth/register",
            json={
                "email": "dup@example.com",
                "password": "strong123",
                "username": "user2",
            },
        )

    assert resp.status_code == status.HTTP_409_CONFLICT


def test_login_ok(client):
    mock_user = _make_mock_user(email="bob@example.com")

    with patch("app.crud.user.user_crud.get_by_email", return_value=mock_user), \
         patch("app.service.auth_service.verify_password", return_value=True):
        resp = client.post(
            "/auth/login",
            json={"email": "bob@example.com", "password": "secret456"},
        )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    mock_user = _make_mock_user(email="bob@example.com")

    with patch("app.crud.user.user_crud.get_by_email", return_value=mock_user), \
         patch("app.service.auth_service.verify_password", return_value=False):
        resp = client.post(
            "/auth/login",
            json={"email": "bob@example.com", "password": "wrong"},
        )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    with patch("app.crud.user.user_crud.get_by_email", return_value=None):
        resp = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "anything"},
        )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_ok(client):
    mock_token = _make_mock_refresh_token()

    with patch(
        "app.crud.refresh_token.refresh_token_crud.get_by_token_hash",
        return_value=mock_token,
    ), patch(
        "app.crud.refresh_token.refresh_token_crud.create",
        return_value=MagicMock(),
    ):
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": "valid-refresh-token"},
        )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_invalid_token(client):
    with patch(
        "app.crud.refresh_token.refresh_token_crud.get_by_token_hash",
        return_value=None,
    ):
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": "garbage"},
        )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_revoked_token(client):
    mock_token = _make_mock_refresh_token(
        revoked_at=datetime.now(timezone.utc)
    )

    with patch(
        "app.crud.refresh_token.refresh_token_crud.get_by_token_hash",
        return_value=mock_token,
    ):
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": "revoked-token"},
        )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_expired_token(client):
    mock_token = _make_mock_refresh_token(
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )

    with patch(
        "app.crud.refresh_token.refresh_token_crud.get_by_token_hash",
        return_value=mock_token,
    ):
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": "expired-token"},
        )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_ok(client):
    mock_token = _make_mock_refresh_token()

    with patch(
        "app.crud.refresh_token.refresh_token_crud.get_by_token_hash",
        return_value=mock_token,
    ):
        resp = client.post(
            "/auth/logout",
            json={"refresh_token": "valid-refresh-token"},
        )

    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_logout_invalid_token(client):
    with patch(
        "app.crud.refresh_token.refresh_token_crud.get_by_token_hash",
        return_value=None,
    ):
        resp = client.post(
            "/auth/logout",
            json={"refresh_token": "garbage"},
        )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
