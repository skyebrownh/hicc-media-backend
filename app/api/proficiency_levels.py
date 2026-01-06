from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.db.models import ProficiencyLevel, ProficiencyLevelCreate, ProficiencyLevelUpdate 
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_404

router = APIRouter(prefix="/proficiency_levels")

@router.get("", response_model=list[ProficiencyLevel])
async def get_all_proficiency_levels(session: Session = Depends(get_db_session)):
    """Get all proficiency levels"""
    return session.exec(select(ProficiencyLevel)).all()

@router.get("/{id}", response_model=ProficiencyLevel)
async def get_single_proficiency_level(id: UUID, session: Session = Depends(get_db_session)):
    """Get a proficiency level by ID"""
    return get_or_404(session, ProficiencyLevel, id)

@router.post("", response_model=ProficiencyLevel, status_code=status.HTTP_201_CREATED)
async def post_proficiency_level(proficiency_level: ProficiencyLevelCreate, session: Session = Depends(get_db_session)):
    """Create a new proficiency level"""
    new_proficiency_level = ProficiencyLevel.model_validate(proficiency_level)
    try:
        session.add(new_proficiency_level)
        session.commit()
        session.refresh(new_proficiency_level)
        return new_proficiency_level
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

# @router.patch("/{proficiency_level_id}", response_model=ProficiencyLevelOut)
# async def patch_proficiency_level(
#     proficiency_level_id: UUID,
#     proficiency_level_update: ProficiencyLevelUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_proficiency_level(conn, proficiency_level_id=proficiency_level_id, payload=proficiency_level_update)

@router.delete("/{id}")
async def delete_proficiency_level(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a proficiency level by ID"""
    proficiency_level = session.get(ProficiencyLevel, id)
    if not proficiency_level:
        return Response(status_code=status.HTTP_204_NO_CONTENT) # Proficiency level not found, nothing to delete
    session.delete(proficiency_level)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Proficiency level deleted successfully
