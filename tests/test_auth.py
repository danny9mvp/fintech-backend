from unittest.mock import MagicMock, patch

from fastapi import status


def _make_mock_user(id=1, email="test@test.com", username="test", pwd_hash="hashed"):
    u = MagicMock()
    u.id = id
    u.email = email
    u.username = username
    u.pwd_hash = pwd_hash
    return u


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
         patch("app.api.auth_controller.verify_password", return_value=True):
        resp = client.post(
            "/auth/login",
            json={"email": "bob@example.com", "password": "secret456"},
        )

    assert resp.status_code == status.HTTP_200_OK
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    mock_user = _make_mock_user(email="bob@example.com")

    with patch("app.crud.user.user_crud.get_by_email", return_value=mock_user), \
         patch("app.api.auth_controller.verify_password", return_value=False):
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
