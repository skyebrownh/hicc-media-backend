from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import ProficiencyLevel, ProficiencyLevelCreate, ProficiencyLevelUpdate 
from app.utils.dependencies import SessionDep, ProficiencyLevelDep
from app.services.domain import create_object, update_object

router = APIRouter(prefix="/proficiency_levels")

@router.get("", response_model=list[ProficiencyLevel])
def get_all_proficiency_levels(session: SessionDep):
    return session.exec(select(ProficiencyLevel)).all()

@router.get("/{id}", response_model=ProficiencyLevel)
def get_single_proficiency_level(proficiency_level: ProficiencyLevelDep):
    return proficiency_level

@router.post("", response_model=ProficiencyLevel, status_code=status.HTTP_201_CREATED)
def post_proficiency_level(payload: ProficiencyLevelCreate, session: SessionDep):
    return create_object(session, payload, ProficiencyLevel)

@router.patch("/{id}", response_model=ProficiencyLevel)
def patch_proficiency_level(payload: ProficiencyLevelUpdate, session: SessionDep, proficiency_level: ProficiencyLevelDep):
    return update_object(session, payload, proficiency_level)

@router.delete("/{id}")
def delete_proficiency_level(session: SessionDep, proficiency_level: ProficiencyLevelDep):
    session.delete(proficiency_level)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
