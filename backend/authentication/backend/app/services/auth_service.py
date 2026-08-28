from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.utils.validators import is_valid_email, normalize_email, validate_password


class AuthService:
    @staticmethod
    def register_user(db: Session, *, name: str, email: str, password: str, role: str = "TEAM_MEMBER") -> User:
        normalized_email = normalize_email(email)
        if not name or not name.strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Name is required")
        if not is_valid_email(normalized_email):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email address")
        if not validate_password(password):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 8 characters, include letters and numbers")
        try:
            user_role = UserRole(role.upper())
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid role") from exc
        if db.query(User).filter(User.email == normalized_email).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed_password = hash_password(password)
        user = User(
            name=name.strip(),
            email=normalized_email,
            password_hash=hashed_password,
            role=user_role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, *, email: str, password: str) -> User:
        normalized_email = normalize_email(email)
        user = db.query(User).filter(User.email == normalized_email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")
        return user

    @staticmethod
    def issue_token_for_user(user: User) -> str:
        return create_access_token(subject=str(user.id), role=user.role.value)
