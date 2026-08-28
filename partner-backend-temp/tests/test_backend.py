from datetime import date, timedelta
from app.core.auth import CurrentUser
from app.main import app
from app.core.auth import get_current_user

def auth(user_id=1,role='PROJECT_MANAGER'):
    async def current(): return CurrentUser(user_id,role)
    app.dependency_overrides[get_current_user]=current

def test_project_task_milestone_dependency_dashboard(client):
    auth();
    p=client.post('/api/projects',json={'name':'Alpha'}).json(); pid=p['id']
    assert client.post(f'/api/projects/{pid}/members',json={'user_id':2}).status_code==201
    m=client.post(f'/api/projects/{pid}/milestones',json={'name':'M1'}).json()
    t1=client.post(f'/api/projects/{pid}/tasks',json={'title':'Build','milestone_id':m['id'],'due_date':str(date.today()-timedelta(days=1))}).json()
    t2=client.post(f'/api/projects/{pid}/tasks',json={'title':'Test'}).json()
    assert client.post(f"/api/tasks/{t1['id']}/dependencies",json={'depends_on_task_id':t2['id']}).status_code==201
    assert client.post(f"/api/tasks/{t1['id']}/dependencies",json={'depends_on_task_id':t2['id']}).status_code==409
    assert client.post(f"/api/tasks/{t1['id']}/dependencies",json={'depends_on_task_id':t1['id']}).status_code==400
    data=client.get(f'/api/projects/{pid}/dashboard').json()
    assert data['total_tasks']==2 and data['overdue_tasks']==1 and data['project_member_count']==1

def test_viewer_cannot_modify_and_unauthenticated_rejected(client):
    app.dependency_overrides.pop(get_current_user,None)
    assert client.get('/api/projects').status_code==401
    auth(3,'VIEWER')
    assert client.post('/api/projects',json={'name':'Nope'}).status_code==403
