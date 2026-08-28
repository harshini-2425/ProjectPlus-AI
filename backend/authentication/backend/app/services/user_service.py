from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.user import User
from backend.app.utils.validators import normalize_email, is_valid_email, validate_password


class UserService:

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    @staticmethod
    def update_current_user(
        db: Session,
        user: User,
        *,
        name: str | None,
        email: str | None,
        password: str | None
    ):
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database session is required")

        # Re-fetch the user using the current database session.
        # This ensures the object is persistent in this Session.
        db_user = db.query(User).filter(User.id == user.id).first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update name
        if name is not None:
            name = name.strip()

            if not name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Name cannot be empty"
                )

            db_user.name = name

        # Update email
        if email is not None:
            normalized = normalize_email(email)
            if not is_valid_email(normalized):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email address")
            db_user.email = normalized

        # Update password
        if password is not None:
            if not validate_password(password):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 8 characters, include letters and numbers")
            db_user.password_hash = hash_password(password)

        # Save changes
        db.commit()

        # Refresh the object that belongs to THIS session
        db.refresh(db_user)

        return db_user