from uuid import UUID
import asyncpg
from fastapi import APIRouter, Depends, Body, status
from app.models import MediaRoleCreate, MediaRoleUpdate, MediaRoleOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_media_role, update_media_role
from app.db.database import get_db_connection

router = APIRouter(prefix="/media_roles")

@router.get("", response_model=list[MediaRoleOut])
async def get_media_roles(conn: asyncpg.Connection = Depends(get_db_connection)):
        return await fetch_all(conn, table="media_roles")

@router.get("/{media_role_id}", response_model=MediaRoleOut)
async def get_media_role(media_role_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
        return await fetch_one(conn, table="media_roles", filters={"media_role_id": media_role_id})

@router.post("", response_model=MediaRoleOut, status_code=status.HTTP_201_CREATED)
async def post_media_role(media_role: MediaRoleCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
        return await insert_media_role(conn, media_role=media_role)

@router.patch("/{media_role_id}", response_model=MediaRoleOut)
async def patch_media_role(
    media_role_id: UUID,
    media_role_update: MediaRoleUpdate | None = Body(default=None),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
        return await update_media_role(conn, media_role_id=media_role_id, payload=media_role_update)

@router.delete("/{media_role_id}", response_model=MediaRoleOut)
async def delete_media_role(media_role_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
        return await delete_one(conn, table="media_roles", filters={"media_role_id": media_role_id})
