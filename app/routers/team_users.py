from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import TeamUser, TeamUserCreate, TeamUserUpdate, TeamUserPublic, Team, User
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session

router = APIRouter()

# Get all users for a team
@router.get("/teams/{team_id}/users", response_model=list[TeamUserPublic])
async def get_team_users_for_team(team_id: UUID, session: Session = Depends(get_db_session)):
    team = session.exec(
        select(Team)
        .where(Team.id == team_id)
        .options(
            selectinload(Team.team_users)
            .selectinload(TeamUser.user))
        ).one_or_none()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return [
        TeamUserPublic(
            id=tu.id,
            team_id=tu.team_id,
            user_id=tu.user_id,
            is_active=tu.is_active,
            team_name=team.name,
            team_code=team.code,
            team_is_active=team.is_active,
            user_first_name=tu.user.first_name,
            user_last_name=tu.user.last_name,
            user_email=tu.user.email,
            user_phone=tu.user.phone,
            user_is_active=tu.user.is_active,
        )
        for tu in team.team_users
    ]

# # Get single team user
# @router.get("/teams/{team_id}/users/{user_id}", response_model=TeamUserOut)
# async def get_team_user(team_id: UUID, user_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await fetch_one(conn, table="team_users", filters={"team_id": team_id, "user_id": user_id})

# # Insert new team user
# @router.post("/team_users", response_model=TeamUserOut, status_code=status.HTTP_201_CREATED)
# async def post_team_user(team_user: TeamUserCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_team_user(conn, team_user=team_user)

# # Update a team user
# @router.patch("/teams/{team_id}/users/{user_id}", response_model=TeamUserOut)
# async def patch_team_user(
#     team_id: UUID,
#     user_id: UUID,
#     team_user_update: TeamUserUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_team_user(conn, team_id=team_id, user_id=user_id, payload=team_user_update)

# # Delete a team user
# @router.delete("/teams/{team_id}/users/{user_id}", response_model=TeamUserOut)
# async def delete_team_user(team_id: UUID, user_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="team_users", filters={"team_id": team_id, "user_id": user_id})