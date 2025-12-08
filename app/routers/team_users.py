from fastapi import APIRouter, Depends, status
from app.models import TeamUserCreate, TeamUserUpdate, TeamUserOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_team_user
from app.db.database import get_db_pool

router = APIRouter(prefix="/team_users")

@router.get("/", response_model=list[TeamUserOut])
async def get_team_users(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="team_users")

@router.get("/{id}", response_model=TeamUserOut)
async def get_team_user(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="team_users", id=id)

@router.post("/", response_model=TeamUserOut, status_code=status.HTTP_201_CREATED)
async def post_team_user(team_user: TeamUserCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_team_user(conn, team_user=team_user)

# @router.patch("/{id}", response_model=TeamUserOut)
# async def update_team_user(id: str, team_user: TeamUserUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="team_users", body=team_user.model_dump(exclude_none=True), id=id)

@router.delete("/{id}", response_model=TeamUserOut)
async def delete_team_user(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="team_users", id=id)