from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user
from backend.app.models.team import Team
from backend.app.models.user import User, UserRole
from backend.app.schemas.team import TeamCreate, TeamMemberOut, TeamOut, TeamUpdate
from backend.app.services.team_service import TeamService

router = APIRouter()


@router.post("", response_model=TeamOut, status_code=status.HTTP_201_CREATED, summary="Create a team")
def create_team(payload: TeamCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in {UserRole.ADMIN, UserRole.PROJECT_MANAGER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    team = TeamService.create_team(db, name=payload.name, description=payload.description, created_by=current_user.id)
    return TeamOut(id=team.id, name=team.name, description=team.description, created_by=team.created_by)


@router.get("", response_model=list[TeamOut], summary="List teams")
def list_teams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in {UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.TEAM_MEMBER, UserRole.VIEWER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    teams = TeamService.list_teams(db)
    return [TeamOut(id=team.id, name=team.name, description=team.description, created_by=team.created_by) for team in teams]


@router.get("/{team_id}", response_model=TeamOut, summary="Get team")
def get_team(team_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = TeamService.get_team(db, team_id)
    if current_user.role == UserRole.TEAM_MEMBER and not any(member.user_id == current_user.id for member in team.members):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role == UserRole.VIEWER and not any(member.user_id == current_user.id for member in team.members):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return TeamOut(id=team.id, name=team.name, description=team.description, created_by=team.created_by)


@router.put("/{team_id}", response_model=TeamOut, summary="Update team")
def update_team(team_id: int, payload: TeamUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = TeamService.get_team(db, team_id)
    if current_user.role != UserRole.ADMIN and team.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated_team = TeamService.update_team(db, team, name=payload.name, description=payload.description)
    return TeamOut(id=updated_team.id, name=updated_team.name, description=updated_team.description, created_by=updated_team.created_by)


@router.delete("/{team_id}", summary="Delete team")
def delete_team(team_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = TeamService.get_team(db, team_id)
    if current_user.role != UserRole.ADMIN and team.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    TeamService.delete_team(db, team)
    return {"detail": "Team deleted"}


@router.post("/{team_id}/members/{user_id}", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED, summary="Add team member")
def add_member_to_team(team_id: int, user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = TeamService.get_team(db, team_id)
    if current_user.role != UserRole.ADMIN and team.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    membership = TeamService.add_member(db, team=team, user_id=user_id)
    return TeamMemberOut(id=membership.id, team_id=membership.team_id, user_id=membership.user_id)


@router.get("/{team_id}/members", response_model=list[TeamMemberOut], summary="List team members")
def list_team_members(team_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = TeamService.get_team(db, team_id)
    if current_user.role != UserRole.ADMIN and team.created_by != current_user.id and not any(member.user_id == current_user.id for member in team.members):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    memberships = TeamService.list_members(db, team)
    return [TeamMemberOut(id=member.id, team_id=member.team_id, user_id=member.user_id) for member in memberships]


@router.delete("/{team_id}/members/{user_id}", summary="Remove team member")
def remove_member_from_team(team_id: int, user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = TeamService.get_team(db, team_id)
    if current_user.role != UserRole.ADMIN and team.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    TeamService.remove_member(db, team=team, user_id=user_id)
    return {"detail": "Team member removed"}
