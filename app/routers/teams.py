from fastapi import APIRouter, Depends, status
from app.models import TeamCreate, TeamUpdate, TeamOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_team
from app.db.database import get_db_pool

router = APIRouter(prefix="/teams")

@router.get("/", response_model=list[TeamOut])
async def get_teams(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="teams")

@router.get("/{id}", response_model=TeamOut)
async def get_team(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="teams", id=id)

@router.post("/", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
async def post_team(team: TeamCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_team(conn, team=team)

# @router.patch("/{id}", response_model=TeamOut)
# async def update_team(id: str, user: TeamUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="teams", body=user.model_dump(exclude_none=True), id=id)

@router.delete("/{id}", response_model=TeamOut)
async def delete_team(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="teams", id=id)