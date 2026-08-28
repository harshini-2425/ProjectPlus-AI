from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.core.config import settings
from backend.app.db.database import get_db
from backend.app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


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
