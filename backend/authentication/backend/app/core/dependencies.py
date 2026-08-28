from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.database import SessionLocal
from backend.app.models.user import User


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user


def require_project_manager(current_user: User = Depends(get_current_user)):
    if current_user.role.value not in {"ADMIN", "PROJECT_MANAGER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user


def require_manager_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.value not in {"ADMIN", "PROJECT_MANAGER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user


def require_authenticated(current_user: User = Depends(get_current_user)):
    return current_user
