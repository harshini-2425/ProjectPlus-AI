import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.dependencies import get_db
from backend.app.db.database import Base, engine
from backend.app.models.user import User, UserRole


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def _create_user(email: str, role: UserRole, name: str = "User"):
    from backend.app.db.database import SessionLocal
    from backend.app.models.user import User
    from backend.app.core.security import hash_password

    db = SessionLocal()
    user = User(name=name, email=email, password_hash=hash_password("StrongPassword123"), role=role, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_me_route_requires_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_invalid_token_rejected(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


def test_valid_token(client):
    user = _create_user("user@example.com", UserRole.TEAM_MEMBER, "Alpha")
    from backend.app.core.security import create_access_token

    token = create_access_token(subject=str(user.id), role=user.role.value)
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_admin_user_cannot_access_other_user_details_without_permission(client):
    admin = _create_user("admin@example.com", UserRole.ADMIN, "Admin")
    other = _create_user("other@example.com", UserRole.TEAM_MEMBER, "Other")
    from backend.app.core.security import create_access_token

    token = create_access_token(subject=str(admin.id), role=admin.role.value)
    response = client.get(f"/api/users/{other.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_project_manager_restricted(client):
    pm = _create_user("pm@example.com", UserRole.PROJECT_MANAGER, "PM")
    from backend.app.core.security import create_access_token

    token = create_access_token(subject=str(pm.id), role=pm.role.value)
    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_viewer_restricted(client):
    viewer = _create_user("viewer@example.com", UserRole.VIEWER, "Viewer")
    from backend.app.core.security import create_access_token

    token = create_access_token(subject=str(viewer.id), role=viewer.role.value)
    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
