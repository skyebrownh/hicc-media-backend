from fastapi import APIRouter, Depends, status
from app.models import ScheduleDateRoleCreate, ScheduleDateRoleUpdate, ScheduleDateRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_schedule_date_role, update_schedule_date_role
from app.db.database import get_db_pool

router = APIRouter(prefix="/schedule_date_roles")

@router.get("/", response_model=list[ScheduleDateRoleOut])
async def get_schedule_date_roles(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedule_date_roles")

@router.get("/{id}", response_model=ScheduleDateRoleOut)
async def get_schedule_date_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedule_date_roles", id=id)

@router.post("/", response_model=ScheduleDateRoleOut, status_code=status.HTTP_201_CREATED)
async def post_schedule_date_role(schedule_date_role: ScheduleDateRoleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_schedule_date_role(conn, schedule_date_role=schedule_date_role)

@router.patch("/{id}", response_model=ScheduleDateRoleOut)
async def patch_schedule_date_role(id: str, schedule_date_role: ScheduleDateRoleUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_schedule_date_role(conn, schedule_date_role_id=id, payload=schedule_date_role)

@router.delete("/{id}", response_model=ScheduleDateRoleOut)
async def delete_schedule_date_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="schedule_date_roles", id=id)