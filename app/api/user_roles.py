from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException, Response
from app.db.models import UserRole, UserRoleUpdate, UserRolePublic, User, Role, ProficiencyLevel
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.services.queries import get_user_for_user_roles, get_role_for_user_roles

router = APIRouter()

@router.get("/users/{user_id}/roles", response_model=list[UserRolePublic])
async def get_roles_for_user(user_id: UUID, session: Session = Depends(get_db_session)):
    """Get all roles for a user"""
    user = get_user_for_user_roles(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return [
        UserRolePublic.from_objects(
            user_role=ur,
            user=user,
            role=ur.role,
            proficiency_level=ur.proficiency_level,
        )
        for ur in user.user_roles
    ]

@router.get("/roles/{role_id}/users", response_model=list[UserRolePublic])
async def get_users_for_role(role_id: UUID, session: Session = Depends(get_db_session)):
    """Get all users for a role"""
    role = get_role_for_user_roles(session, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return [
        UserRolePublic.from_objects(
            user_role=ur,
            user=ur.user,
            role=role,
            proficiency_level=ur.proficiency_level,
        )
        for ur in role.user_roles
    ]

# User roles are not created or deleted directly through an API endpoint - they are created when a user or role is created (same with delete)

# # Update a user role
# @router.patch("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
# async def patch_user_role(user_id: UUID, role_id: UUID, user_role_update: UserRoleUpdate | None = Body(default=None), conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await update_user_role(conn, user_id=user_id, role_id=role_id, payload=user_role_update)