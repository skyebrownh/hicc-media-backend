from fastapi import APIRouter, Depends, status
from app.models import ScheduleCreate, ScheduleUpdate, ScheduleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_schedule, update_schedule
from app.db.database import get_db_pool

router = APIRouter(prefix="/schedules")

@router.get("", response_model=list[ScheduleOut])
async def get_schedules(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedules")

@router.get("/{id}", response_model=ScheduleOut)
async def get_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedules", id=id)

@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
async def post_schedule(schedule: ScheduleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_schedule(conn, schedule=schedule)

@router.patch("/{id}", response_model=ScheduleOut)
async def patch_schedule(id: str, schedule: ScheduleUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_schedule(conn, schedule_id=id, payload=schedule)

@router.delete("/{id}", response_model=ScheduleOut)
async def delete_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="schedules", id=id)