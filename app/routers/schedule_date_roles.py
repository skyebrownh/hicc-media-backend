from fastapi import APIRouter, Depends, status

from app.models.schedule_date_role import ScheduleDateRoleCreate, ScheduleDateRoleUpdate, ScheduleDateRoleOut 
from app.db.queries import fetch_all, fetch_one
from app.db.db import get_db_pool

router = APIRouter(prefix="/schedule_date_roles")

@router.get("/", response_model=list[ScheduleDateRoleOut])
async def get_schedule_date_roles(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedule_date_roles")

@router.get("/{id}", response_model=ScheduleDateRoleOut)
async def get_schedule_date_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedule_date_roles", id=id)

# @router.post("/", response_model=ScheduleDateRoleOut, status_code=status.HTTP_201_CREATED)
# async def post_schedule_date_roles(schedule_date_role: ScheduleDateRoleCreate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.post(table="schedule_date_roles", body=schedule_date_role.model_dump(exclude_none=True))

# @router.patch("/{id}", response_model=ScheduleDateRoleOut)
# async def update_schedule_date_role(id: str, schedule_date_role: ScheduleDateRoleUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="schedule_date_roles", body=schedule_date_role.model_dump(exclude_none=True), id=id)

# @router.delete("/{id}", response_model=ScheduleDateRoleOut)
# async def delete_schedule_date_role(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="schedule_date_roles", id=id)