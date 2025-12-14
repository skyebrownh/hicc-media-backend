import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.models import UserAvailabilityCreate, UserAvailabilityUpdate, UserAvailabilityOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_availability, insert_user_availabilities, update_user_availability
from app.db.database import get_db_pool

router = APIRouter()

# Get all user availabilities
@router.get("/user_availability", response_model=list[UserAvailabilityOut])
async def get_user_availability(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="user_availability")

# Get single user availability
@router.get("/users/{user_id}/dates/{date}", response_model=UserAvailabilityOut)
async def get_user_availability(user_id: UUID, date: datetime.date, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="user_availability", filters={"user_id": user_id, "date": date})

# Insert new user availability
@router.post("/user_availability", response_model=UserAvailabilityOut, status_code=status.HTTP_201_CREATED)
async def post_user_availability(user_availability: UserAvailabilityCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_availability(conn, user_availability=user_availability)

# Insert user availabilities in bulk for a user
@router.post("/user_availability/bulk", response_model=list[UserAvailabilityOut], status_code=status.HTTP_201_CREATED)
async def post_user_availabilities_bulk(user_availabilities: list[UserAvailabilityCreate], pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_availabilities(conn, user_availabilities=user_availabilities)

# Update user availability date
@router.patch("/users/{user_id}/dates/{date}", response_model=UserAvailabilityOut)
async def patch_user_availability(
    user_id: UUID,
    date: datetime.date,
    user_availability_update: UserAvailabilityUpdate | None = Body(default=None),
    pool=Depends(get_db_pool),
):
    async with pool.acquire() as conn:
        return await update_user_availability(conn, user_id=user_id, date=date, payload=user_availability_update)

# Delete user availability
@router.delete("/users/{user_id}/dates/{date}", response_model=UserAvailabilityOut)
async def delete_user_availability(user_id: UUID, date: datetime.date, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="user_availability", filters={"user_id": user_id, "date": date})