from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
class Dependency(Base):
    __tablename__='dependencies'
    __table_args__=(UniqueConstraint('task_id','depends_on_task_id',name='uq_task_dependency'),)
    id: Mapped[int]=mapped_column(primary_key=True,index=True)
    task_id: Mapped[int]=mapped_column(ForeignKey('tasks.id',ondelete='CASCADE'),index=True)
    depends_on_task_id: Mapped[int]=mapped_column(ForeignKey('tasks.id',ondelete='CASCADE'),index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    task=relationship('Task',foreign_keys=[task_id])
    depends_on=relationship('Task',foreign_keys=[depends_on_task_id])
