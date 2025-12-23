from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from sqlmodel import Session, select
from app.db.models import ProficiencyLevel, ProficiencyLevelCreate, ProficiencyLevelUpdate 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_proficiency_level, update_proficiency_level
from app.utils.dependencies import get_db_session

router = APIRouter(prefix="/proficiency_levels")

@router.get("", response_model=list[ProficiencyLevel])
async def get_proficiency_levels(session: Session = Depends(get_db_session)):
    return session.exec(select(ProficiencyLevel)).all()

# @router.get("/{proficiency_level_id}", response_model=ProficiencyLevelOut)
# async def get_proficiency_level(proficiency_level_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await fetch_one(conn, table="proficiency_levels", filters={"proficiency_level_id": proficiency_level_id})

# @router.post("", response_model=ProficiencyLevelOut, status_code=status.HTTP_201_CREATED)
# async def post_proficiency_level(proficiency_level: ProficiencyLevelCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_proficiency_level(conn, proficiency_level=proficiency_level)

# @router.patch("/{proficiency_level_id}", response_model=ProficiencyLevelOut)
# async def patch_proficiency_level(
#     proficiency_level_id: UUID,
#     proficiency_level_update: ProficiencyLevelUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_proficiency_level(conn, proficiency_level_id=proficiency_level_id, payload=proficiency_level_update)

# @router.delete("/{proficiency_level_id}", response_model=ProficiencyLevelOut)
# async def delete_proficiency_level(proficiency_level_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="proficiency_levels", filters={"proficiency_level_id": proficiency_level_id})
