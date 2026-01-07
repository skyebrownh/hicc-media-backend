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

# @router.patch("/{team_id}", response_model=TeamOut)
# async def patch_team(team_id: UUID, team_update: TeamUpdate | None = Body(default=None), conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await update_team(conn, team_id=team_id, payload=team_update)

@router.delete("/{id}")
async def delete_team(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a team by ID"""
    team = get_team(session, id)
    raise_exception_if_not_found(team, Team, status.HTTP_204_NO_CONTENT) # Team not found, nothing to delete
    session.delete(team)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Team deleted successfully