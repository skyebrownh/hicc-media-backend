from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.db.models import Team, TeamCreate, TeamUpdate, TeamUser
from app.utils.dependencies import get_db_session
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter(prefix="/teams")

@router.get("", response_model=list[Team])
def get_all_teams(session: Session = Depends(get_db_session)):
    """Get all teams"""
    return session.exec(select(Team)).all()

@router.get("/{id}", response_model=Team)
def get_single_team(id: UUID, session: Session = Depends(get_db_session)):
    """Get a team by ID"""
    team = session.get(Team, id)
    raise_exception_if_not_found(team, Team)
    return team

@router.post("", response_model=Team, status_code=status.HTTP_201_CREATED)
def post_team(team: TeamCreate, session: Session = Depends(get_db_session)):
    """Create a new team"""
    new_team = Team.model_validate(team)
    try:
        session.add(new_team)
        session.commit()
        session.refresh(new_team)
        return new_team
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.patch("/{id}", response_model=Team)
def update_team(id: UUID, payload: TeamUpdate, session: Session = Depends(get_db_session)):
    """Update a team by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    team = session.get(Team, id)
    raise_exception_if_not_found(team, Team)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(team, key, value)
    try:
        # no need to add the team again, it's already in the session from raise_exception_if_not_found
        session.commit()
        session.refresh(team)
        return team
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/{id}")
def delete_team(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a team by ID"""
    team = session.exec(select(Team).where(Team.id == id).options(selectinload(Team.team_users).selectinload(TeamUser.user))).one_or_none()
    raise_exception_if_not_found(team, Team, status.HTTP_204_NO_CONTENT) # Team not found, nothing to delete
    session.delete(team)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Team deleted successfully