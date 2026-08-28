from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.auth import RegisterUser, TokenResponse, UserOut
from backend.app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a user account and store a bcrypt password hash in PostgreSQL.",
)
def register_user(payload: RegisterUser, db: Session = Depends(get_db)):
    user = AuthService.register_user(
        db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT",
    description="Authenticate a user with email/password and return a bearer token.",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, email=form_data.username, password=form_data.password)
    token = AuthService.issue_token_for_user(user)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
        },
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get authenticated user",
    description="Retrieve the currently authenticated user's profile.",
)
def get_authenticated_user(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
    )
