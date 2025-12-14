from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.models import UserRoleCreate, UserRoleUpdate, UserRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_role, insert_all_roles_for_user, insert_all_users_for_role, update_user_role
from app.db.database import get_db_pool

router = APIRouter()

# Get all roles for a user
@router.get("/users/{user_id}/roles", response_model=list[UserRoleOut])
async def get_roles_for_user(user_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        await fetch_one(conn, table="users", filters={"user_id": user_id})
        return await fetch_all(conn, table="user_roles", filters={"user_id": user_id})
    
# Get all users for a role
@router.get("/roles/{role_id}/users", response_model=list[UserRoleOut])
async def get_users_for_role(role_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        await fetch_one(conn, table="media_roles", filters={"media_role_id": role_id})
        return await fetch_all(conn, table="user_roles", filters={"media_role_id": role_id})
    
# Get single user role
@router.get("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
async def get_role_for_user(user_id: UUID, role_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="user_roles", filters={"user_id": user_id, "media_role_id": role_id})

# Insert all roles for a user
@router.post("/users/{user_id}/roles", response_model=list[UserRoleOut], status_code=status.HTTP_201_CREATED)
async def post_roles_for_user(user_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        await fetch_one(conn, table="users", filters={"user_id": user_id})
        return await insert_all_roles_for_user(conn, user_id=user_id)

# Insert all users for a role
@router.post("/roles/{role_id}/users", response_model=list[UserRoleOut], status_code=status.HTTP_201_CREATED)
async def post_users_for_role(role_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        await fetch_one(conn, table="media_roles", filters={"media_role_id": role_id})
        return await insert_all_users_for_role(conn, role_id=role_id)

# Insert new user role
@router.post("/user_roles", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
async def post_user_role(user_role: UserRoleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_role(conn, user_role=user_role)

# Update a user role
@router.patch("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
async def patch_user_role(user_id: UUID, role_id: UUID, user_role_update: UserRoleUpdate | None = Body(default=None), pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_user_role(conn, user_id=user_id, role_id=role_id, payload=user_role_update)

# Delete a user role
@router.delete("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
async def delete_user_role(user_id: UUID, role_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="user_roles", filters={"user_id": user_id, "media_role_id": role_id})