from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.models import ProficiencyLevelCreate, ProficiencyLevelUpdate, ProficiencyLevelOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_proficiency_level, update_proficiency_level
from app.db.database import get_db_pool

router = APIRouter(prefix="/proficiency_levels")

@router.get("", response_model=list[ProficiencyLevelOut])
async def get_proficiency_levels(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="proficiency_levels")

@router.get("/{proficiency_level_id}", response_model=ProficiencyLevelOut)
async def get_proficiency_level(proficiency_level_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="proficiency_levels", filters={"proficiency_level_id": proficiency_level_id})

@router.post("", response_model=ProficiencyLevelOut, status_code=status.HTTP_201_CREATED)
async def post_proficiency_level(proficiency_level: ProficiencyLevelCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_proficiency_level(conn, proficiency_level=proficiency_level)

@router.patch("/{proficiency_level_id}", response_model=ProficiencyLevelOut)
async def patch_proficiency_level(proficiency_level_id: UUID, proficiency_level_update: ProficiencyLevelUpdate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await update_proficiency_level(conn, proficiency_level_id=proficiency_level_id, payload=proficiency_level_update)

@router.delete("/{proficiency_level_id}", response_model=ProficiencyLevelOut)
async def delete_proficiency_level(proficiency_level_id: UUID, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="proficiency_levels", filters={"proficiency_level_id": proficiency_level_id})
