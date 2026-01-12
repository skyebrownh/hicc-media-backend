from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.db.models import TeamUser, TeamUserCreate, TeamUserUpdate, TeamUserPublic, Team
from app.utils.dependencies import get_db_session
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter()

@router.get("/teams/{team_id}/users", response_model=list[TeamUserPublic])
def get_team_users_for_team(team_id: UUID, session: Session = Depends(get_db_session)):
    """Get all users for a team"""
    team = session.exec(select(Team).where(Team.id == team_id).options(selectinload(Team.team_users).selectinload(TeamUser.user))).one_or_none()
    raise_exception_if_not_found(team, Team)
    return [
        TeamUserPublic.from_objects(team_user=tu, team=team, user=tu.user)
        for tu in team.team_users
    ]

@router.post("/teams/{team_id}/users", response_model=TeamUser, status_code=status.HTTP_201_CREATED)
def add_user_to_team(team_id: UUID, payload: TeamUserCreate, session: Session = Depends(get_db_session)):
    """Add a user to a team"""
    team = session.exec(select(Team).where(Team.id == team_id).options(selectinload(Team.team_users).selectinload(TeamUser.user))).one_or_none()
    raise_exception_if_not_found(team, Team)
    new_team_user = TeamUser(team_id=team_id, user_id=payload.user_id, is_active=payload.is_active)
    try:
        session.add(new_team_user)
        session.commit()
        session.refresh(new_team_user)
        return new_team_user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.patch("/teams/{team_id}/users/{user_id}", response_model=TeamUserPublic)
def update_team_user(team_id: UUID, user_id: UUID, payload: TeamUserUpdate, session: Session = Depends(get_db_session)):
    """Update a team user by team ID and user ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    team_user = session.exec(select(TeamUser).where(TeamUser.team_id == team_id).where(TeamUser.user_id == user_id)).one_or_none()
    raise_exception_if_not_found(team_user, TeamUser)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(team_user, key, value)
    try:
        # no need to add the team user again, it's already in the session from get_team_user
        session.commit()
        session.refresh(team_user)
        return TeamUserPublic.from_objects(team_user=team_user, team=team_user.team, user=team_user.user)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/teams/{team_id}/users/{user_id}")
def delete_team_user(team_id: UUID, user_id: UUID, session: Session = Depends(get_db_session)):
    """Delete a team user by team ID and user ID"""
    team_user = session.exec(select(TeamUser).where(TeamUser.team_id == team_id).where(TeamUser.user_id == user_id)).one_or_none()
    raise_exception_if_not_found(team_user, TeamUser, status.HTTP_204_NO_CONTENT) # Team user not found, nothing to delete
    session.delete(team_user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Team user deleted successfully