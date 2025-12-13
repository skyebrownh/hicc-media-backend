from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.models import UserAvailabilityCreate, UserAvailabilityUpdate, UserAvailabilityOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_availability, update_user_availability
from app.db.database import get_db_pool

router = APIRouter(prefix="/user_availability")

# Get all user availabilities
@router.get("", response_model=list[UserAvailabilityOut])
async def get_user_availability(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="user_availability")

# Get single user availability
@router.get("/{user_availability_id}", response_model=UserAvailabilityOut)
async def get_user_availability(user_availability_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="user_availability", filters={"user_availability_id": user_availability_id})

# TODO: Insert user availabilities in bulk for a user

# Insert new user availability
@router.post("", response_model=UserAvailabilityOut, status_code=status.HTTP_201_CREATED)
async def post_user_availability(user_availability: UserAvailabilityCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_availability(conn, user_availability=user_availability)

# Update user availability date
@router.patch("/{user_availability_id}", response_model=UserAvailabilityOut)
async def patch_user_availability(
    user_availability_id: UUID,
    user_availability_update: UserAvailabilityUpdate | None = Body(default=None),
    pool=Depends(get_db_pool),
):
    async with pool.acquire() as conn:
        return await update_user_availability(conn, user_availability_id=user_availability_id, payload=user_availability_update)

# Delete user availability
@router.delete("/{user_availability_id}", response_model=UserAvailabilityOut)
async def delete_user_availability(user_availability_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="user_availability", filters={"user_availability_id": user_availability_id})