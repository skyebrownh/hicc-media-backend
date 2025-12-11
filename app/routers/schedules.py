from fastapi import APIRouter, Depends, status
from app.models import ScheduleCreate, ScheduleUpdate, ScheduleOut, ScheduleDateOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_schedule, update_schedule, delete_all
from app.db.database import get_db_pool

router = APIRouter(prefix="/schedules")

# Get all schedules
@router.get("", response_model=list[ScheduleOut])
async def get_schedules(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedules")
    
# Get all schedule_dates for a schedule
@router.get("/{id}/schedule_dates", response_model=list[ScheduleDateOut])
async def get_schedule_dates_for_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedule_dates", filters={"schedule_id": id})

# Get single schedule
@router.get("/{id}", response_model=ScheduleOut)
async def get_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedules", filters={"schedule_id": id})

# Insert new schedule
@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
async def post_schedule(schedule: ScheduleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_schedule(conn, schedule=schedule)
    
# TODO: Insert schedule dates for a schedule based on configuration

# Update schedule
@router.patch("/{id}", response_model=ScheduleOut)
async def patch_schedule(id: str, schedule_update: ScheduleUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_schedule(conn, schedule_id=id, payload=schedule_update)

# Delete schedule
@router.delete("/{id}", response_model=ScheduleOut)
async def delete_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="schedules", filters={"schedule_id": id})
    
# Delete schedule dates for a schedule
@router.delete("/{id}/schedule_dates", response_model=list[ScheduleDateOut])
async def delete_schedule_dates_for_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_all(conn, table="schedule_dates", filters={"schedule_id": id})