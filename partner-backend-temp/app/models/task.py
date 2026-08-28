from datetime import date, datetime, timezone
from enum import Enum
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class TaskStatus(str, Enum): TODO='TODO'; IN_PROGRESS='IN_PROGRESS'; BLOCKED='BLOCKED'; DONE='DONE'
class TaskPriority(str, Enum): LOW='LOW'; MEDIUM='MEDIUM'; HIGH='HIGH'; CRITICAL='CRITICAL'
class Task(Base):
    __tablename__='tasks'
    id: Mapped[int]=mapped_column(primary_key=True,index=True)
    project_id: Mapped[int]=mapped_column(ForeignKey('projects.id',ondelete='CASCADE'),index=True)
    milestone_id: Mapped[int|None]=mapped_column(ForeignKey('milestones.id',ondelete='SET NULL'),index=True)
    title: Mapped[str]=mapped_column(String(200),nullable=False)
    description: Mapped[str|None]=mapped_column(Text)
    status: Mapped[TaskStatus]=mapped_column(String(30),default=TaskStatus.TODO,nullable=False)
    priority: Mapped[TaskPriority]=mapped_column(String(30),default=TaskPriority.MEDIUM,nullable=False)
    assigned_to: Mapped[int|None]=mapped_column(ForeignKey('users.id',ondelete='SET NULL'),index=True)
    due_date: Mapped[date|None]=mapped_column(Date)
    created_by: Mapped[int]=mapped_column(ForeignKey('users.id'),index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))
    project=relationship('Project',back_populates='tasks')
    milestone=relationship('Milestone',back_populates='tasks')
