from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.models import MediaRoleCreate, MediaRoleUpdate, MediaRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_media_role, update_media_role
from app.db.database import get_db_pool

router = APIRouter(prefix="/media_roles")

@router.get("", response_model=list[MediaRoleOut])
async def get_media_roles(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="media_roles")

@router.get("/{media_role_id}", response_model=MediaRoleOut)
async def get_media_role(media_role_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="media_roles", filters={"media_role_id": media_role_id})

@router.post("", response_model=MediaRoleOut, status_code=status.HTTP_201_CREATED)
async def post_media_role(media_role: MediaRoleCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_media_role(conn, media_role=media_role)

@router.patch("/{media_role_id}", response_model=MediaRoleOut)
async def patch_media_role(media_role_id: UUID, media_role_update: MediaRoleUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_media_role(conn, media_role_id=media_role_id, payload=media_role_update)

@router.delete("/{media_role_id}", response_model=MediaRoleOut)
async def delete_media_role(media_role_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="media_roles", filters={"media_role_id": media_role_id})
