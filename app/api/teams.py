from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.db.models import Team, TeamCreate, TeamUpdate
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_raise_exception, raise_exception_if_not_found
from app.services.queries import get_team

router = APIRouter(prefix="/teams")

@router.get("", response_model=list[Team])
async def get_all_teams(session: Session = Depends(get_db_session)):
    """Get all teams"""
    return session.exec(select(Team)).all()

@router.get("/{id}", response_model=Team)
async def get_single_team(id: UUID, session: Session = Depends(get_db_session)):
    """Get a team by ID"""
    return get_or_raise_exception(session, Team, id)

@router.post("", response_model=Team, status_code=status.HTTP_201_CREATED)
async def post_team(team: TeamCreate, session: Session = Depends(get_db_session)):
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
async def update_team(id: UUID, payload: TeamUpdate, session: Session = Depends(get_db_session)):
    """Update a team by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    team = get_or_raise_exception(session, Team, id)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(team, key, value)
    try:
        # no need to add the team again, it's already in the session from get_or_raise_exception
        session.commit()
        session.refresh(team)
        return team
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/{id}")
async def delete_team(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a team by ID"""
    team = get_team(session, id)
    raise_exception_if_not_found(team, Team, status.HTTP_204_NO_CONTENT) # Team not found, nothing to delete
    session.delete(team)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Team deleted successfully