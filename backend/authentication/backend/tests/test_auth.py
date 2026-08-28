import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.dependencies import get_db
from backend.app.db.database import Base, engine
from backend.app.models.user import UserRole


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Teja",
            "email": "teja@example.com",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "teja@example.com"
    assert body["role"] == "TEAM_MEMBER"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Teja",
            "email": "teja@example.com",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Another",
            "email": "teja@example.com",
            "password": "AnotherPass123",
            "role": "VIEWER",
        },
    )
    assert response.status_code == 400


def test_register_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Bad",
            "email": "not-an-email",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    assert response.status_code == 422


def test_register_weak_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Weak",
            "email": "weak@example.com",
            "password": "short",
            "role": "TEAM_MEMBER",
        },
    )
    assert response.status_code == 422


def test_register_missing_fields(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Missing"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Teja",
            "email": "teja@example.com",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "teja@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "teja@example.com"


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Teja",
            "email": "teja@example.com",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "teja@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "missing@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401


def test_login_inactive_user(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "John",
            "email": "john@example.com",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    from backend.app.db.database import SessionLocal
    from backend.app.models.user import User

    db = SessionLocal()
    user = db.query(User).filter(User.email == "john@example.com").first()
    user.is_active = False
    db.commit()
    db.close()

    response = client.post(
        "/api/auth/login",
        data={"username": "john@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 401
