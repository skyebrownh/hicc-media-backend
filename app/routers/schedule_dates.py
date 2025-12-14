from uuid import UUID
import asyncpg
from fastapi import APIRouter, Depends, Body, status
from app.models import ScheduleDateCreate, ScheduleDateUpdate, ScheduleDateOut, ScheduleDateRoleOut, UserDateOut
from app.db.queries import fetch_all, fetch_one, delete_one, delete_all, insert_schedule_date, update_schedule_date
from app.db.database import get_db_connection

router = APIRouter(prefix="/schedule_dates")

# Get all schedule dates
@router.get("", response_model=list[ScheduleDateOut])
async def get_schedule_dates(conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_all(conn, table="schedule_dates")
    
# Get all schedule_date_roles for a schedule date
@router.get("/{schedule_date_id}/roles", response_model=list[ScheduleDateRoleOut])
async def get_all_schedule_date_roles_by_schedule_date(schedule_date_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    await fetch_one(conn, table="schedule_dates", filters={"schedule_date_id": schedule_date_id})
    return await fetch_all(conn, table="schedule_date_roles", filters={"schedule_date_id": schedule_date_id})
    
# Get all user dates for a schedule date
@router.get("/{schedule_date_id}/user_dates", response_model=list[UserDateOut])
async def get_all_user_dates_by_schedule_date(schedule_date_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    schedule_date = await fetch_one(conn, table="schedule_dates", filters={"schedule_date_id": schedule_date_id})
    return await fetch_all(conn, table="user_dates", filters={"date": schedule_date["date"]})
    
# Get single schedule date
@router.get("/{schedule_date_id}", response_model=ScheduleDateOut)
async def get_schedule_date(schedule_date_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_one(conn, table="schedule_dates", filters={"schedule_date_id": schedule_date_id})

# Insert new schedule date
@router.post("", response_model=ScheduleDateOut, status_code=status.HTTP_201_CREATED)
async def post_schedule_date(schedule_date: ScheduleDateCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await insert_schedule_date(conn, schedule_date=schedule_date)
    
# TODO: Insert schedule date roles for a schedule date based on configuration

# Update schedule date
@router.patch("/{schedule_date_id}", response_model=ScheduleDateOut)
async def patch_schedule_date(
    schedule_date_id: UUID,
    schedule_date_update: ScheduleDateUpdate | None = Body(default=None),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    return await update_schedule_date(conn, schedule_date_id=schedule_date_id, payload=schedule_date_update)

# Delete schedule date
@router.delete("/{schedule_date_id}", response_model=ScheduleDateOut)
async def delete_schedule_date(schedule_date_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await delete_one(conn, table="schedule_dates", filters={"schedule_date_id": schedule_date_id})
    
# Delete schedule date roles for a schedule date
@router.delete("/{schedule_date_id}/roles", response_model=list[ScheduleDateRoleOut])
async def delete_schedule_date_roles_for_schedule_date(schedule_date_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    await fetch_one(conn, table="schedule_dates", filters={"schedule_date_id": schedule_date_id})
    return await delete_all(conn, table="schedule_date_roles", filters={"schedule_date_id": schedule_date_id})