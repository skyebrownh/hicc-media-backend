import datetime
from uuid import UUID
import asyncpg
from fastapi import APIRouter, Depends, Body, status
from app.models import UserDateCreate, UserDateUpdate, UserDateOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_date, insert_user_dates, update_user_date
from app.db.database import get_db_connection

# No prefix - this router uses mixed URL patterns:
# - /user_dates for collection operations (GET all, POST, POST bulk)
# - /users/{user_id}/dates/{date} for resource operations (GET, PATCH, DELETE)
router = APIRouter()

# Get all user dates
@router.get("/user_dates", response_model=list[UserDateOut])
async def get_user_dates(conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_all(conn, table="user_dates")

# Get single user date
@router.get("/users/{user_id}/dates/{date}", response_model=UserDateOut)
async def get_user_date(user_id: UUID, date: datetime.date, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_one(conn, table="user_dates", filters={"user_id": user_id, "date": date})

# Insert new user date
@router.post("/user_dates", response_model=UserDateOut, status_code=status.HTTP_201_CREATED)
async def post_user_date(user_date: UserDateCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await insert_user_date(conn, user_date=user_date)

# Insert user dates in bulk for a user
@router.post("/user_dates/bulk", response_model=list[UserDateOut], status_code=status.HTTP_201_CREATED)
async def post_user_dates_bulk(user_dates: list[UserDateCreate], conn: asyncpg.Connection = Depends(get_db_connection)):
    return await insert_user_dates(conn, user_dates=user_dates)

# Update user date
@router.patch("/users/{user_id}/dates/{date}", response_model=UserDateOut)
async def patch_user_date(
    user_id: UUID,
    date: datetime.date,
    user_date_update: UserDateUpdate | None = Body(default=None),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    return await update_user_date(conn, user_id=user_id, date=date, payload=user_date_update)

# Delete user date
@router.delete("/users/{user_id}/dates/{date}", response_model=UserDateOut)
async def delete_user_date(user_id: UUID, date: datetime.date, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await delete_one(conn, table="user_dates", filters={"user_id": user_id, "date": date})
