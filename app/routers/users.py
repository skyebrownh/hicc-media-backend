from uuid import UUID
import asyncpg
from fastapi import APIRouter, Depends, Body, status
from app.models import UserCreate, UserUpdate, UserOut
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user, update_user
from app.db.database import get_db_connection

router = APIRouter(prefix="/users")

@router.get("", response_model=list[UserOut])
async def get_users(conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_all(conn, table="users")

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await fetch_one(conn, table="users", filters={"user_id": user_id})

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def post_user(user: UserCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await insert_user(conn, user=user)

@router.patch("/{user_id}", response_model=UserOut)
async def patch_user(
    user_id: UUID,
    user_update: UserUpdate | None = Body(default=None),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    return await update_user(conn, user_id=user_id, payload=user_update)

@router.delete("/{user_id}", response_model=UserOut)
async def delete_user(user_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await delete_one(conn, table="users", filters={"user_id": user_id})