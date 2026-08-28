from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db, require_admin, require_authenticated
from backend.app.core.security import get_current_user
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserResponse, UserUpdate
from backend.app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="Get my profile")
def read_my_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
def read_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in {UserRole.ADMIN, UserRole.PROJECT_MANAGER} and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    user = UserService.get_user_by_id(db, user_id)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
    )


@router.get("", response_model=list[UserResponse], summary="List users")
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in {UserRole.ADMIN, UserRole.PROJECT_MANAGER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    users = UserService.get_all_users(db)
    return [
        UserResponse(id=user.id, name=user.name, email=user.email, role=user.role.value, is_active=user.is_active) for user in users
    ]


@router.put("/me", response_model=UserResponse, summary="Update my profile")
def update_my_profile(payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_user = UserService.update_current_user(
        db,
        current_user,
        name=payload.name,
        email=payload.email,
        password=payload.password,
    )
    return UserResponse(
        id=updated_user.id,
        name=updated_user.name,
        email=updated_user.email,
        role=updated_user.role.value,
        is_active=updated_user.is_active,
    )
