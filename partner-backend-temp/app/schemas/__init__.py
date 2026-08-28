from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.project import ProjectStatus
from app.models.task import TaskStatus, TaskPriority

class ProjectCreate(BaseModel):
	name: str = Field(min_length=1, max_length=150)
	description: str | None = None
	status: ProjectStatus = ProjectStatus.PLANNING
	start_date: date | None = None
	end_date: date | None = None

	@model_validator(mode='after')
	def dates_valid(self):
		if self.start_date and self.end_date and self.end_date < self.start_date:
			raise ValueError('end_date must not precede start_date')
		return self

class ProjectUpdate(ProjectCreate):
	pass

class ProjectOut(ProjectCreate):
	id: int
	created_by: int
	model_config = ConfigDict(from_attributes=True)

class MemberCreate(BaseModel):
	user_id: int
	role: str = Field(default='TEAM_MEMBER', min_length=1, max_length=30)

class MemberUpdate(BaseModel):
	role: str = Field(min_length=1, max_length=30)

class MemberOut(MemberCreate):
	id: int
	project_id: int
	model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
	title: str = Field(min_length=1, max_length=200)
	description: str | None = None
	milestone_id: int | None = None
	status: TaskStatus = TaskStatus.TODO
	priority: TaskPriority = TaskPriority.MEDIUM
	assigned_to: int | None = None
	due_date: date | None = None

class TaskUpdate(TaskCreate):
	pass

class TaskOut(TaskCreate):
	id: int
	project_id: int
	created_by: int
	model_config = ConfigDict(from_attributes=True)

class MilestoneCreate(BaseModel):
	name: str = Field(min_length=1, max_length=150)
	description: str | None = None
	due_date: date | None = None
	status: str = 'PENDING'

class MilestoneUpdate(MilestoneCreate):
	pass

class MilestoneOut(MilestoneCreate):
	id: int
	project_id: int
	model_config = ConfigDict(from_attributes=True)

class DependencyCreate(BaseModel):
	depends_on_task_id: int

class DependencyOut(DependencyCreate):
	id: int
	task_id: int
	model_config = ConfigDict(from_attributes=True)