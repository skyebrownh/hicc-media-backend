from fastapi import APIRouter, Depends, status

from app.models.user import UserCreate, UserUpdate, UserOut
from app.db.queries import fetch_all, fetch_one
from app.db.db import get_db_pool

router = APIRouter(prefix="/users")

@router.get("/", response_model=list[UserOut])
async def get_users(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="users")

@router.get("/{id}", response_model=UserOut)
async def get_user(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="users", id=id)

# @router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
# async def post_users(user: UserCreate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.post(table="users", body=user.model_dump(exclude_none=True))

# @router.patch("/{id}", response_model=UserOut)
# async def update_user(id: str, user: UserUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="users", body=user.model_dump(exclude_none=True), id=id)

# @router.delete("/{id}", response_model=UserOut)
# async def delete_user(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="users", id=id)