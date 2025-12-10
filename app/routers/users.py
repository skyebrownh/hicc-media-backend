from fastapi import APIRouter, Depends, status
from app.models import UserCreate, UserUpdate, UserOut
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user, update_user
from app.db.database import get_db_pool

router = APIRouter(prefix="/users")

@router.get("", response_model=list[UserOut])
async def get_users(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="users")

@router.get("/{id}", response_model=UserOut)
async def get_user(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="users", id=id)

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def post_user(user: UserCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user(conn, user=user)

@router.patch("/{id}", response_model=UserOut)
async def patch_user(id: str, user: UserUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_user(conn, user_id=id, payload=user)

@router.delete("/{id}", response_model=UserOut)
async def delete_user(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="users", id=id)