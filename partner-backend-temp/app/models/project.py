from datetime import date, datetime, timezone
from enum import Enum
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ProjectStatus(str, Enum):
    PLANNING='PLANNING'; ACTIVE='ACTIVE'; ON_HOLD='ON_HOLD'; COMPLETED='COMPLETED'; CANCELLED='CANCELLED'

class Project(Base):
    __tablename__='projects'
    id: Mapped[int]=mapped_column(primary_key=True, index=True)
    name: Mapped[str]=mapped_column(String(150), nullable=False)
    description: Mapped[str|None]=mapped_column(Text)
    status: Mapped[ProjectStatus]=mapped_column(String(30), default=ProjectStatus.PLANNING, nullable=False)
    start_date: Mapped[date|None]=mapped_column(Date)
    end_date: Mapped[date|None]=mapped_column(Date)
    created_by: Mapped[int]=mapped_column(ForeignKey('users.id'), index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    members=relationship('ProjectMember', back_populates='project', cascade='all, delete-orphan')
    tasks=relationship('Task', back_populates='project', cascade='all, delete-orphan')
    milestones=relationship('Milestone', back_populates='project', cascade='all, delete-orphan')
