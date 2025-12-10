from fastapi import APIRouter, Depends, status
from app.models import ScheduleDateCreate, ScheduleDateUpdate, ScheduleDateOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_schedule_date, update_schedule_date
from app.db.database import get_db_pool

router = APIRouter(prefix="/schedule_dates")

@router.get("", response_model=list[ScheduleDateOut])
async def get_schedule_dates(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedule_dates")

@router.get("/{id}", response_model=ScheduleDateOut)
async def get_schedule_date(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedule_dates", id=id)

@router.post("", response_model=ScheduleDateOut, status_code=status.HTTP_201_CREATED)
async def post_schedule_date(schedule_date: ScheduleDateCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_schedule_date(conn, schedule_date=schedule_date)

@router.patch("/{id}", response_model=ScheduleDateOut)
async def patch_schedule_date(id: str, schedule_date: ScheduleDateUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_schedule_date(conn, schedule_date_id=id, payload=schedule_date)

@router.delete("/{id}", response_model=ScheduleDateOut)
async def delete_schedule_date(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="schedule_dates", id=id)