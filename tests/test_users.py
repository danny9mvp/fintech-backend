from fastapi import status


def test_get_me(client, auth_header):
    resp = client.get("/users/me", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data


def test_get_me_unauthorized(client):
    resp = client.get("/users/me")
    assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
