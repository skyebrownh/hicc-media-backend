from fastapi import APIRouter, Depends, status
from app.models import UserRoleCreate, UserRoleUpdate, UserRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_role
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

# @router.patch("/{id}", response_model=UserRoleOut)
# async def update_user_role(id: str, user_role: UserRoleUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="user_roles", body=user_role.model_dump(exclude_none=True), id=id)

@router.delete("/{id}", response_model=UserRoleOut)
async def delete_user_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="user_roles", id=id)