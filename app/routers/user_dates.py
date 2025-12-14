import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.models import UserDateCreate, UserDateUpdate, UserDateOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_date, insert_user_dates, update_user_date
from app.db.database import get_db_pool

router = APIRouter()

# Get all user dates
@router.get("/user_dates", response_model=list[UserDateOut])
async def get_user_dates(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="user_dates")

# Get single user date
@router.get("/users/{user_id}/dates/{date}", response_model=UserDateOut)
async def get_user_date(user_id: UUID, date: datetime.date, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="user_dates", filters={"user_id": user_id, "date": date})

# Insert new user date
@router.post("/user_dates", response_model=UserDateOut, status_code=status.HTTP_201_CREATED)
async def post_user_date(user_date: UserDateCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_date(conn, user_date=user_date)

# Insert user dates in bulk for a user
@router.post("/user_dates/bulk", response_model=list[UserDateOut], status_code=status.HTTP_201_CREATED)
async def post_user_dates_bulk(user_dates: list[UserDateCreate], pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_dates(conn, user_dates=user_dates)

# Update user date
@router.patch("/users/{user_id}/dates/{date}", response_model=UserDateOut)
async def patch_user_date(
    user_id: UUID,
    date: datetime.date,
    user_date_update: UserDateUpdate | None = Body(default=None),
    pool=Depends(get_db_pool),
):
    async with pool.acquire() as conn:
        return await update_user_date(conn, user_id=user_id, date=date, payload=user_date_update)

# Delete user date
@router.delete("/users/{user_id}/dates/{date}", response_model=UserDateOut)
async def delete_user_date(user_id: UUID, date: datetime.date, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="user_dates", filters={"user_id": user_id, "date": date})
