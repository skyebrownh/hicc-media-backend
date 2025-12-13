from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.models import TeamUserCreate, TeamUserUpdate, TeamUserOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_team_user, update_team_user
from app.db.database import get_db_pool

router = APIRouter()

# Get all team users
@router.get("/team_users", response_model=list[TeamUserOut])
async def get_team_users(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="team_users")

# Get all users for a team
@router.get("/teams/{team_id}/users", response_model=list[TeamUserOut])
async def get_team_users_for_team(team_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        await fetch_one(conn, table="teams", filters={"team_id": team_id})
        return await fetch_all(conn, table="team_users", filters={"team_id": team_id})
    
# Get single team user
@router.get("/teams/{team_id}/users/{user_id}", response_model=TeamUserOut)
async def get_team_user(team_id: UUID, user_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="team_users", filters={"team_id": team_id, "user_id": user_id})

# Insert new team user
@router.post("/team_users", response_model=TeamUserOut, status_code=status.HTTP_201_CREATED)
async def post_team_user(team_user: TeamUserCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_team_user(conn, team_user=team_user)

# Update a team user
@router.patch("/teams/{team_id}/users/{user_id}", response_model=TeamUserOut)
async def patch_team_user(
    team_id: UUID,
    user_id: UUID,
    team_user_update: TeamUserUpdate | None = Body(default=None),
    pool=Depends(get_db_pool),
):
    async with pool.acquire() as conn:
        return await update_team_user(conn, team_id=team_id, user_id=user_id, payload=team_user_update)

# Delete a team user
@router.delete("/teams/{team_id}/users/{user_id}", response_model=TeamUserOut)
async def delete_team_user(team_id: UUID, user_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="team_users", filters={"team_id": team_id, "user_id": user_id})