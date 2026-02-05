from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import ProficiencyLevel, ProficiencyLevelCreate, ProficiencyLevelUpdate 
from app.utils.dependencies import SessionDep, ProficiencyLevelDep, default_depends, default_depends_with_admin
from app.services.domain import create_object, update_object, delete_object

router = APIRouter(prefix="/proficiency_levels", tags=["proficiency_levels"])

@router.get("", response_model=list[ProficiencyLevel], dependencies=default_depends())
def get_all_proficiency_levels(session: SessionDep):
    return session.exec(select(ProficiencyLevel)).all()

@router.get("/{id}", response_model=ProficiencyLevel, dependencies=default_depends())
def get_single_proficiency_level(proficiency_level: ProficiencyLevelDep):
    return proficiency_level

@router.post("", response_model=ProficiencyLevel, status_code=status.HTTP_201_CREATED, dependencies=default_depends_with_admin())
def post_proficiency_level(payload: ProficiencyLevelCreate, session: SessionDep):
    return create_object(session, payload, ProficiencyLevel)

@router.patch("/{id}", response_model=ProficiencyLevel, dependencies=default_depends_with_admin())
def patch_proficiency_level(payload: ProficiencyLevelUpdate, session: SessionDep, proficiency_level: ProficiencyLevelDep):
    return update_object(session, payload, proficiency_level)

@router.delete("/{id}", dependencies=default_depends_with_admin())
def delete_proficiency_level(session: SessionDep, proficiency_level: ProficiencyLevelDep):
    delete_object(session, proficiency_level)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
