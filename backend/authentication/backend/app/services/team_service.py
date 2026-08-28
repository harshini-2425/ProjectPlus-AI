from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.team import Team
from backend.app.models.team_member import TeamMember
from backend.app.models.user import User, UserRole


class TeamService:
    @staticmethod
    def create_team(db: Session, *, name: str, description: str | None, created_by: int):
        team = Team(name=name, description=description, created_by=created_by)
        db.add(team)
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def get_team(db: Session, team_id: int):
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        return team

    @staticmethod
    def list_teams(db: Session):
        return db.query(Team).all()

    @staticmethod
    def update_team(db: Session, team: Team, *, name: str | None, description: str | None):
        if name is not None:
            team.name = name
        if description is not None:
            team.description = description
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def delete_team(db: Session, team: Team):
        db.delete(team)
        db.commit()
        return True

    @staticmethod
    def add_member(db: Session, *, team: Team, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        existing = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == user_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already in team")
        team_member = TeamMember(team_id=team.id, user_id=user_id)
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
        return team_member

    @staticmethod
    def remove_member(db: Session, *, team: Team, user_id: int):
        membership = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == user_id).first()
        if not membership:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")
        db.delete(membership)
        db.commit()
        return True

    @staticmethod
    def list_members(db: Session, team: Team):
        return db.query(TeamMember).filter(TeamMember.team_id == team.id).all()

    @staticmethod
    def can_manage_team(current_user: User, team: Team) -> bool:
        if current_user.role == UserRole.ADMIN:
            return True
        if current_user.role == UserRole.PROJECT_MANAGER and team.created_by == current_user.id:
            return True
        return False
