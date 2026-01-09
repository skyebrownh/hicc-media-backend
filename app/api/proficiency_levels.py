from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.db.models import ProficiencyLevel, ProficiencyLevelCreate, ProficiencyLevelUpdate 
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_raise_exception

router = APIRouter(prefix="/proficiency_levels")

@router.get("", response_model=list[ProficiencyLevel])
async def get_all_proficiency_levels(session: Session = Depends(get_db_session)):
    """Get all proficiency levels"""
    return session.exec(select(ProficiencyLevel)).all()

@router.get("/{id}", response_model=ProficiencyLevel)
async def get_single_proficiency_level(id: UUID, session: Session = Depends(get_db_session)):
    """Get a proficiency level by ID"""
    return get_or_raise_exception(session, ProficiencyLevel, id)

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

@router.patch("/{id}", response_model=ProficiencyLevel)
async def update_proficiency_level(id: UUID, payload: ProficiencyLevelUpdate, session: Session = Depends(get_db_session)):
    """Update a proficiency level by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    proficiency_level = get_or_raise_exception(session, ProficiencyLevel, id)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(proficiency_level, key, value)
    try:
        # no need to add the role again, it's already in the session from get_or_raise_exception
        session.commit()
        session.refresh(proficiency_level)
        return proficiency_level
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/{id}")
async def delete_proficiency_level(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a proficiency level by ID"""
    proficiency_level = get_or_raise_exception(session, ProficiencyLevel, id, status.HTTP_204_NO_CONTENT) # Proficiency level not found, nothing to delete
    session.delete(proficiency_level)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Proficiency level deleted successfully
