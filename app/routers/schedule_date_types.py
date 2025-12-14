from uuid import UUID
import asyncpg
from fastapi import APIRouter, Depends, Body, status
from app.models import ScheduleDateTypeCreate, ScheduleDateTypeUpdate, ScheduleDateTypeOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_schedule_date_type, update_schedule_date_type
from app.db.database import get_db_connection

router = APIRouter(prefix="/schedule_date_types")

@router.get("", response_model=list[ScheduleDateTypeOut])
async def get_schedule_date_types(conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_all(conn, table="schedule_date_types")

@router.get("/{schedule_date_type_id}", response_model=ScheduleDateTypeOut)
async def get_schedule_date_type(schedule_date_type_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_one(conn, table="schedule_date_types", filters={"schedule_date_type_id": schedule_date_type_id})

@router.post("", response_model=ScheduleDateTypeOut, status_code=status.HTTP_201_CREATED)
async def post_schedule_date_type(schedule_date_type: ScheduleDateTypeCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await insert_schedule_date_type(conn, schedule_date_type=schedule_date_type)

@router.patch("/{schedule_date_type_id}", response_model=ScheduleDateTypeOut)
async def patch_schedule_date_type(
    schedule_date_type_id: UUID,
    schedule_date_type_update: ScheduleDateTypeUpdate | None = Body(default=None),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    return await update_schedule_date_type(conn, schedule_date_type_id=schedule_date_type_id, payload=schedule_date_type_update)

@router.delete("/{schedule_date_type_id}", response_model=ScheduleDateTypeOut)
async def delete_schedule_date_type(schedule_date_type_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await delete_one(conn, table="schedule_date_types", filters={"schedule_date_type_id": schedule_date_type_id})