from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import Role, RoleCreate, RoleUpdate
from app.utils.dependencies import SessionDep, RoleDep, default_depends, default_depends_with_admin
from app.services.domain import create_role_with_user_roles, update_object, delete_object

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("", response_model=list[Role], dependencies=default_depends())
def get_all_roles(session: SessionDep):
    return session.exec(select(Role)).all()

@router.get("/{id}", response_model=Role, dependencies=default_depends())
def get_single_role(role: RoleDep):
    return role

@router.post("", response_model=Role, status_code=status.HTTP_201_CREATED, dependencies=default_depends_with_admin())
def post_role(payload: RoleCreate, session: SessionDep):
    return create_role_with_user_roles(session, payload)

@router.patch("/{id}", response_model=Role, dependencies=default_depends_with_admin())
def patch_role(payload: RoleUpdate, session: SessionDep, role: RoleDep):
    return update_object(session, payload, role)

@router.delete("/{id}", dependencies=default_depends_with_admin())
def delete_role(session: SessionDep, role: RoleDep):
    delete_object(session, role)
    return Response(status_code=status.HTTP_204_NO_CONTENT)