from fastapi import APIRouter, Depends, status
from app.models import UserRoleCreate, UserRoleUpdate, UserRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_role, update_user_role
from app.db.database import get_db_pool

router = APIRouter()

# Get all roles for a user
@router.get("/users/{user_id}/roles", response_model=list[UserRoleOut])
async def get_roles_for_user(user_id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="user_roles", filters={"user_id": user_id})
    
# Get all users for a role
@router.get("/roles/{role_id}/users", response_model=list[UserRoleOut])
async def get_users_for_role(role_id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="user_roles", filters={"media_role_id": role_id})
    
# Get single user role
@router.get("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
async def get_role_for_user(user_id: str, role_id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="user_roles", filters={"user_id": user_id, "media_role_id": role_id})

# Insert all roles for a user
@router.post("/users/{user_id}/roles", response_model=list[UserRoleOut], status_code=status.HTTP_201_CREATED)
async def post_roles_for_user(user_id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        # TODO: Insert all roles for user_id
        pass

# Insert all users for a role
@router.post("/roles/{role_id}/users", response_model=list[UserRoleOut], status_code=status.HTTP_201_CREATED)
async def post_users_for_role(role_id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        # TODO: Insert all users for role_id
        pass

# Insert new user role
@router.post("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
async def post_user_role(user_role: UserRoleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        # TODO: Refactor to insert based on join IDs in the path
        return await insert_user_role(conn, user_role=user_role)

# Update proficiency level of a user role
@router.patch("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
async def patch_user_role(user_id: str, role_id: str, user_role_update: UserRoleUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        # TODO: Refactor to update based on join IDs in the path
        return await update_user_role(conn, user_role_id=id, payload=user_role_update)

@router.delete("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
async def delete_user_role(user_id: str, role_id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        # TODO: Refactor to delete based on join IDs in the path
        return await delete_one(conn, table="user_roles", filters={"user_id": user_id, "media_role_id": role_id})