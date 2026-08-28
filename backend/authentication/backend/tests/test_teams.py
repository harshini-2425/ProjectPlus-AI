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


def _login(client, email: str, password: str = "StrongPassword123"):
    response = client.post("/api/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_get_update_delete_team(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Manager",
            "email": "manager@example.com",
            "password": "StrongPassword123",
            "role": "PROJECT_MANAGER",
        },
    )
    token = _login(client, "manager@example.com")

    create_response = client.post(
        "/api/teams",
        json={"name": "Core Team", "description": "Hackathon team"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    team_id = create_response.json()["id"]

    get_response = client.get(f"/api/teams/{team_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_response.status_code == 200

    update_response = client.put(
        f"/api/teams/{team_id}",
        json={"name": "Updated Team", "description": "Updated description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_response.status_code == 200

    delete_response = client.delete(f"/api/teams/{team_id}", headers={"Authorization": f"Bearer {token}"})
    assert delete_response.status_code == 200


def test_add_duplicate_member_and_remove_member(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Manager",
            "email": "manager@example.com",
            "password": "StrongPassword123",
            "role": "PROJECT_MANAGER",
        },
    )
    client.post(
        "/api/auth/register",
        json={
            "name": "Member",
            "email": "member@example.com",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    token = _login(client, "manager@example.com")

    team_response = client.post(
        "/api/teams",
        json={"name": "Core Team", "description": "Hackathon team"},
        headers={"Authorization": f"Bearer {token}"},
    )
    team_id = team_response.json()["id"]

    add_response = client.post(
        f"/api/teams/{team_id}/members/2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert add_response.status_code == 201

    duplicate_response = client.post(
        f"/api/teams/{team_id}/members/2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert duplicate_response.status_code == 400

    list_response = client.get(f"/api/teams/{team_id}/members", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    remove_response = client.delete(
        f"/api/teams/{team_id}/members/2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert remove_response.status_code == 200


def test_unauthorized_team_modification(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Manager",
            "email": "manager@example.com",
            "password": "StrongPassword123",
            "role": "PROJECT_MANAGER",
        },
    )
    client.post(
        "/api/auth/register",
        json={
            "name": "User",
            "email": "user@example.com",
            "password": "StrongPassword123",
            "role": "TEAM_MEMBER",
        },
    )
    manager_token = _login(client, "manager@example.com")
    user_token = _login(client, "user@example.com")

    team_response = client.post(
        "/api/teams",
        json={"name": "Core Team", "description": "Hackathon team"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    team_id = team_response.json()["id"]

    update_response = client.put(
        f"/api/teams/{team_id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert update_response.status_code == 403
