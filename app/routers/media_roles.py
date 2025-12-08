from fastapi import APIRouter, Depends, status
from app.models import MediaRoleCreate, MediaRoleUpdate, MediaRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_media_role
from app.db.database import get_db_pool

router = APIRouter(prefix="/media_roles")

@router.get("/", response_model=list[MediaRoleOut])
async def get_media_roles(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="media_roles")

@router.get("/{id}", response_model=MediaRoleOut)
async def get_media_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="media_roles", id=id)

@router.post("/", response_model=MediaRoleOut, status_code=status.HTTP_201_CREATED)
async def post_media_role(media_role: MediaRoleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_media_role(conn, media_role=media_role)

# @router.patch("/{id}", response_model=MediaRoleOut)
# async def update_media_role(id: str, media_role: MediaRoleUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="media_roles", body=media_role.model_dump(exclude_none=True), id=id)

@router.delete("/{id}", response_model=MediaRoleOut)
async def delete_media_role(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="media_roles", id=id)