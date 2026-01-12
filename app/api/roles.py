from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import Role, RoleCreate, RoleUpdate
from app.utils.dependencies import SessionDep, RoleDep
from app.services.domain import create_role_with_user_roles, update_role

router = APIRouter(prefix="/roles")

@router.get("", response_model=list[Role])
def get_all_roles(session: SessionDep):
    return session.exec(select(Role)).all()

@router.get("/{id}", response_model=Role)
def get_single_role(role: RoleDep):
    return role

@router.post("", response_model=Role, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, session: SessionDep):
    return create_role_with_user_roles(session, payload)

@router.patch("/{id}", response_model=Role)
def patch_role(payload: RoleUpdate, session: SessionDep, role: RoleDep):
    return update_role(session, payload, role)

@router.delete("/{id}")
def delete_role(session: SessionDep, role: RoleDep):
    session.delete(role)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)