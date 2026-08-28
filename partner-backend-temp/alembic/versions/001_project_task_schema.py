"""project task domain schema
Revision ID: 001_project_task_schema
Revises:
"""
from alembic import op
import sqlalchemy as sa
revision='001_project_task_schema'; down_revision='001_initial_auth_schema'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('projects',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('name',sa.String(150),nullable=False),sa.Column('description',sa.Text()),sa.Column('status',sa.String(30),nullable=False),sa.Column('start_date',sa.Date()),sa.Column('end_date',sa.Date()),sa.Column('created_by',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False))
    op.create_index('ix_projects_created_by','projects',['created_by'])
    op.create_table('project_members',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id',ondelete='CASCADE'),nullable=False),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.Column('role',sa.String(30),nullable=False),sa.Column('joined_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False),sa.UniqueConstraint('project_id','user_id',name='uq_project_user'))
    op.create_index('ix_project_members_project_id','project_members',['project_id']); op.create_index('ix_project_members_user_id','project_members',['user_id'])
    op.create_table('milestones',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id',ondelete='CASCADE'),nullable=False),sa.Column('name',sa.String(150),nullable=False),sa.Column('description',sa.Text()),sa.Column('due_date',sa.Date()),sa.Column('status',sa.String(30),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False))
    op.create_index('ix_milestones_project_id','milestones',['project_id'])
    op.create_table('tasks',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id',ondelete='CASCADE'),nullable=False),sa.Column('milestone_id',sa.Integer(),sa.ForeignKey('milestones.id',ondelete='SET NULL')),sa.Column('title',sa.String(200),nullable=False),sa.Column('description',sa.Text()),sa.Column('status',sa.String(30),nullable=False),sa.Column('priority',sa.String(30),nullable=False),sa.Column('assigned_to',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),sa.Column('due_date',sa.Date()),sa.Column('created_by',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False))
    op.create_index('ix_tasks_project_id','tasks',['project_id']); op.create_index('ix_tasks_milestone_id','tasks',['milestone_id']); op.create_index('ix_tasks_assigned_to','tasks',['assigned_to']); op.create_index('ix_tasks_created_by','tasks',['created_by'])
    op.create_table('dependencies',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('task_id',sa.Integer(),sa.ForeignKey('tasks.id',ondelete='CASCADE'),nullable=False),sa.Column('depends_on_task_id',sa.Integer(),sa.ForeignKey('tasks.id',ondelete='CASCADE'),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('CURRENT_TIMESTAMP'),nullable=False),sa.UniqueConstraint('task_id','depends_on_task_id',name='uq_task_dependency'))
    op.create_index('ix_dependencies_task_id','dependencies',['task_id']); op.create_index('ix_dependencies_depends_on_task_id','dependencies',['depends_on_task_id'])

def downgrade():
    op.drop_table('dependencies'); op.drop_table('tasks'); op.drop_table('milestones'); op.drop_table('project_members'); op.drop_table('projects')
