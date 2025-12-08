from fastapi import APIRouter, Depends, status
from app.models import UserRoleCreate, UserRoleUpdate, UserRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_role, update_user_role
from app.db.database import get_db_pool

router = APIRouter(prefix="/user_roles")

@router.get("/", response_model=list[UserRoleOut])
async def get_user_roles(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="user_roles")

@router.get("/{id}", response_model=UserRoleOut)
async def get_user_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="user_roles", id=id)

@router.post("/", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
async def post_user_role(user_role: UserRoleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_role(conn, user_role=user_role)

@router.patch("/{id}", response_model=UserRoleOut)
async def patch_user_role(id: str, user_role: UserRoleUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_user_role(conn, user_role_id=id, payload=user_role)

@router.delete("/{id}", response_model=UserRoleOut)
async def delete_user_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="user_roles", id=id)