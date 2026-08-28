from datetime import date
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import CurrentUser, get_current_user, require_roles
from app.models import Project, ProjectMember, Task, Milestone, Dependency, ProjectStatus, TaskStatus, TaskPriority
from app.schemas import *

app=FastAPI(title='ProjectPulse AI Project and Task API',version='1.0.0')
MANAGERS={'ADMIN','PROJECT_MANAGER'}

def project_or_404(db, project_id):
    obj=db.query(Project).filter(Project.id==project_id).first()
    if not obj: raise HTTPException(404,'Project not found')
    return obj

def member(db, project_id, user_id): return db.query(ProjectMember).filter(ProjectMember.project_id==project_id,ProjectMember.user_id==user_id).first()
def can_read(db,p,u): return u.role in MANAGERS or p.created_by==u.id or member(db,p.id,u.id) is not None
def can_manage(p,u): return u.role in MANAGERS or p.created_by==u.id

def ensure_read(db,p,u):
    if not can_read(db,p,u): raise HTTPException(403,'Project access required')
def ensure_manage(p,u):
    if not can_manage(p,u): raise HTTPException(403,'Project manager access required')

def save(db,obj):
    db.add(obj); db.commit(); db.refresh(obj); return obj

@app.get('/health', tags=['Dashboard'])
def health(): return {'status':'ok'}

@app.post('/api/projects',response_model=ProjectOut,status_code=201,tags=['Projects'],summary='Create a project')
def create_project(payload:ProjectCreate,u:CurrentUser=Depends(require_roles(*MANAGERS)),db:Session=Depends(get_db)):
    return save(db,Project(**payload.model_dump(),created_by=u.id))
@app.get('/api/projects',response_model=list[ProjectOut],tags=['Projects'],summary='List accessible projects')
def list_projects(u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    if u.role in MANAGERS: return db.query(Project).all()
    return db.query(Project).join(ProjectMember,ProjectMember.project_id==Project.id).filter((ProjectMember.user_id==u.id)|(Project.created_by==u.id)).all()
@app.get('/api/projects/{project_id}',response_model=ProjectOut,tags=['Projects'],summary='Get a project')
def get_project(project_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_read(db,p,u); return p
@app.put('/api/projects/{project_id}',response_model=ProjectOut,tags=['Projects'],summary='Update a project')
def update_project(project_id:int,payload:ProjectUpdate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_manage(p,u); [setattr(p,k,v) for k,v in payload.model_dump().items()]; return save(db,p)
@app.delete('/api/projects/{project_id}',tags=['Projects'],summary='Delete a project')
def delete_project(project_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_manage(p,u); db.delete(p); db.commit(); return {'detail':'Project deleted'}

@app.post('/api/projects/{project_id}/members',response_model=MemberOut,status_code=201,tags=['Project Members'],summary='Add project member')
def add_member(project_id:int,payload:MemberCreate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_manage(p,u)
    if member(db,project_id,payload.user_id): raise HTTPException(409,'User is already a project member')
    return save(db,ProjectMember(project_id=project_id,**payload.model_dump()))
@app.get('/api/projects/{project_id}/members',response_model=list[MemberOut],tags=['Project Members'],summary='List project members')
def list_members(project_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_read(db,p,u); return db.query(ProjectMember).filter_by(project_id=project_id).all()
@app.put('/api/projects/{project_id}/members/{user_id}',response_model=MemberOut,tags=['Project Members'],summary='Update project member role')
def update_member(project_id:int,user_id:int,payload:MemberUpdate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_manage(p,u); m=member(db,project_id,user_id)
    if not m: raise HTTPException(404,'Project member not found')
    m.role=payload.role; return save(db,m)
@app.delete('/api/projects/{project_id}/members/{user_id}',tags=['Project Members'],summary='Remove project member')
def remove_member(project_id:int,user_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_manage(p,u); m=member(db,project_id,user_id)
    if not m: raise HTTPException(404,'Project member not found')
    db.delete(m); db.commit(); return {'detail':'Member removed'}

@app.post('/api/projects/{project_id}/tasks',response_model=TaskOut,status_code=201,tags=['Tasks'],summary='Create task')
def create_task(project_id:int,payload:TaskCreate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_read(db,p,u)
    if u.role not in MANAGERS and not member(db,project_id,u.id): raise HTTPException(403,'Project membership required')
    if payload.milestone_id and not db.query(Milestone).filter_by(id=payload.milestone_id,project_id=project_id).first(): raise HTTPException(400,'Milestone does not belong to project')
    return save(db,Task(project_id=project_id,created_by=u.id,**payload.model_dump()))
@app.get('/api/projects/{project_id}/tasks',response_model=list[TaskOut],tags=['Tasks'],summary='List project tasks')
def list_tasks(project_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_read(db,p,u); return db.query(Task).filter_by(project_id=project_id).all()
def task_or_404(db,task_id):
    t=db.query(Task).filter_by(id=task_id).first()
    if not t: raise HTTPException(404,'Task not found')
    return t
def ensure_task_write(t,u):
    if u.role in MANAGERS or t.created_by==u.id or t.assigned_to==u.id: return
    raise HTTPException(403,'Task modification not permitted')
@app.get('/api/tasks/{task_id}',response_model=TaskOut,tags=['Tasks'],summary='Get task')
def get_task(task_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    t=task_or_404(db,task_id); ensure_read(db,t.project,u); return t
@app.put('/api/tasks/{task_id}',response_model=TaskOut,tags=['Tasks'],summary='Update task')
def update_task(task_id:int,payload:TaskUpdate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    t=task_or_404(db,task_id); ensure_read(db,t.project,u); ensure_task_write(t,u)
    if payload.milestone_id and not db.query(Milestone).filter_by(id=payload.milestone_id,project_id=t.project_id).first(): raise HTTPException(400,'Milestone does not belong to project')
    for k,v in payload.model_dump().items(): setattr(t,k,v)
    return save(db,t)
@app.delete('/api/tasks/{task_id}',tags=['Tasks'],summary='Delete task')
def delete_task(task_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    t=task_or_404(db,task_id); ensure_read(db,t.project,u); ensure_task_write(t,u); db.delete(t); db.commit(); return {'detail':'Task deleted'}

@app.post('/api/projects/{project_id}/milestones',response_model=MilestoneOut,status_code=201,tags=['Milestones'],summary='Create milestone')
def create_milestone(project_id:int,payload:MilestoneCreate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_manage(p,u); return save(db,Milestone(project_id=project_id,**payload.model_dump()))
@app.get('/api/projects/{project_id}/milestones',response_model=list[MilestoneOut],tags=['Milestones'],summary='List milestones')
def list_milestones(project_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_read(db,p,u); return db.query(Milestone).filter_by(project_id=project_id).all()
def milestone_or_404(db,id):
    m=db.query(Milestone).filter_by(id=id).first()
    if not m: raise HTTPException(404,'Milestone not found')
    return m
@app.get('/api/milestones/{milestone_id}',response_model=MilestoneOut,tags=['Milestones'],summary='Get milestone')
def get_milestone(milestone_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    m=milestone_or_404(db,milestone_id); ensure_read(db,m.project,u); return m
@app.put('/api/milestones/{milestone_id}',response_model=MilestoneOut,tags=['Milestones'],summary='Update milestone')
def update_milestone(milestone_id:int,payload:MilestoneUpdate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    m=milestone_or_404(db,milestone_id); ensure_manage(m.project,u)
    for k,v in payload.model_dump().items(): setattr(m,k,v)
    return save(db,m)
@app.delete('/api/milestones/{milestone_id}',tags=['Milestones'],summary='Delete milestone')
def delete_milestone(milestone_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    m=milestone_or_404(db,milestone_id); ensure_manage(m.project,u); db.delete(m); db.commit(); return {'detail':'Milestone deleted'}

@app.post('/api/tasks/{task_id}/dependencies',response_model=DependencyOut,status_code=201,tags=['Dependencies'],summary='Create dependency')
def add_dependency(task_id:int,payload:DependencyCreate,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    t=task_or_404(db,task_id); ensure_manage(t.project,u); d=task_or_404(db,payload.depends_on_task_id)
    if t.id==d.id: raise HTTPException(400,'A task cannot depend on itself')
    if t.project_id!=d.project_id: raise HTTPException(400,'Dependency tasks must share a project')
    if db.query(Dependency).filter_by(task_id=t.id,depends_on_task_id=d.id).first(): raise HTTPException(409,'Dependency already exists')
    return save(db,Dependency(task_id=t.id,depends_on_task_id=d.id))
@app.get('/api/tasks/{task_id}/dependencies',response_model=list[DependencyOut],tags=['Dependencies'],summary='List dependencies')
def list_dependencies(task_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    t=task_or_404(db,task_id); ensure_read(db,t.project,u); return db.query(Dependency).filter_by(task_id=task_id).all()
@app.delete('/api/tasks/{task_id}/dependencies/{dependency_id}',tags=['Dependencies'],summary='Delete dependency')
def delete_dependency(task_id:int,dependency_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    t=task_or_404(db,task_id); ensure_manage(t.project,u); d=db.query(Dependency).filter_by(id=dependency_id,task_id=task_id).first()
    if not d: raise HTTPException(404,'Dependency not found')
    db.delete(d); db.commit(); return {'detail':'Dependency deleted'}

@app.get('/api/projects/{project_id}/dashboard',tags=['Dashboard'],summary='Get project dashboard')
def dashboard(project_id:int,u:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    p=project_or_404(db,project_id); ensure_read(db,p,u); tasks=db.query(Task).filter_by(project_id=project_id).all(); today=date.today()
    by_status={s.value:sum(t.status==s.value for t in tasks) for s in TaskStatus}; by_priority={s.value:sum(t.priority==s.value for t in tasks) for s in TaskPriority}
    overdue = sum(bool(t.due_date and t.due_date < today and t.status != TaskStatus.DONE.value) for t in tasks)
    return {'project_id':project_id,'total_tasks':len(tasks),'completed_tasks':by_status['DONE'],'pending_tasks':len(tasks)-by_status['DONE'],'overdue_tasks':overdue,'task_counts_by_status':by_status,'task_counts_by_priority':by_priority,'milestone_summary':{'total':db.query(Milestone).filter_by(project_id=project_id).count(),'completed':db.query(Milestone).filter_by(project_id=project_id,status='COMPLETED').count()},'project_member_count':db.query(ProjectMember).filter_by(project_id=project_id).count()}
