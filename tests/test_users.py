from datetime import datetime, timezone

from fastapi import status


def test_get_me(client):
    from app.api.deps import get_current_user
    from app.model.user import User

    client.app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        email="test@example.com",
        username="testuser",
        pwd_hash="xxx",
        created_at=datetime.now(timezone.utc),
    )

    resp = client.get("/users/me")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data


def test_get_me_unauthorized(client):
    resp = client.get("/users/me")
    assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
