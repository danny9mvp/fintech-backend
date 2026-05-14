from fastapi import status


def test_register(client):
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
    client.post(
        "/auth/register",
        json={
            "email": "dup@example.com",
            "password": "strong123",
            "username": "user1",
        },
    )
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
    client.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "password": "secret456",
            "username": "bob",
        },
    )
    resp = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "secret456"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "password": "secret456",
            "username": "bob",
        },
    )
    resp = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "wrong"},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "anything"},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
