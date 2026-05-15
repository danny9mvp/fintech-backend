import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

engine = create_engine(os.environ["DATABASE_URL"] , echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def token(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "secret123",
            "username": "testuser",
        },
    )
    resp = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    return resp.json()["access_token"]


@pytest.fixture()
def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
