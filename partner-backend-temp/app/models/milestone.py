from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
class Milestone(Base):
    __tablename__='milestones'
    id: Mapped[int]=mapped_column(primary_key=True,index=True)
    project_id: Mapped[int]=mapped_column(ForeignKey('projects.id',ondelete='CASCADE'),index=True)
    name: Mapped[str]=mapped_column(String(150),nullable=False)
    description: Mapped[str|None]=mapped_column(Text)
    due_date: Mapped[date|None]=mapped_column(Date)
    status: Mapped[str]=mapped_column(String(30),default='PENDING',nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))
    project=relationship('Project',back_populates='milestones')
    tasks=relationship('Task',back_populates='milestone')
