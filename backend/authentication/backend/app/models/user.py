from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PROJECT_MANAGER = "PROJECT_MANAGER"
    TEAM_MEMBER = "TEAM_MEMBER"
    VIEWER = "VIEWER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    teams_created: Mapped[list["Team"]] = relationship("Team", back_populates="creator")
    team_memberships: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
