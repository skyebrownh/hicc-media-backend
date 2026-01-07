from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException, Response
from app.db.models import TeamUser, TeamUserCreate, TeamUserUpdate, TeamUserPublic, Team
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from app.utils.dependencies import get_db_session
from app.services.queries import get_team, get_team_user
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter()

@router.get("/teams/{team_id}/users", response_model=list[TeamUserPublic])
async def get_team_users_for_team(team_id: UUID, session: Session = Depends(get_db_session)):
    """Get all users for a team"""
    team = get_team(session, team_id)
    raise_exception_if_not_found(team, Team)
    return [
        TeamUserPublic.from_objects(team_user=tu, team=team, user=tu.user)
        for tu in team.team_users
    ]

@router.post("/teams/{team_id}/users", response_model=TeamUser, status_code=status.HTTP_201_CREATED)
async def add_user_to_team(team_id: UUID, payload: TeamUserCreate, session: Session = Depends(get_db_session)):
    """Add a user to a team"""
    team = get_team(session, team_id)
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

# # Update a team user
# @router.patch("/teams/{team_id}/users/{user_id}", response_model=TeamUserOut)
# async def patch_team_user(
#     team_id: UUID,
#     user_id: UUID,
#     team_user_update: TeamUserUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_team_user(conn, team_id=team_id, user_id=user_id, payload=team_user_update)

@router.delete("/teams/{team_id}/users/{user_id}")
async def delete_team_user(team_id: UUID, user_id: UUID, session: Session = Depends(get_db_session)):
    """Delete a team user by team ID and user ID"""
    team_user = get_team_user(session, team_id, user_id)
    raise_exception_if_not_found(team_user, TeamUser, status.HTTP_204_NO_CONTENT) # Team user not found, nothing to delete
    session.delete(team_user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Team user deleted successfully