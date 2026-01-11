from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import UserRoleUpdate, UserRolePublic, User, Role, UserRole
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter()

@router.get("/users/{user_id}/roles", response_model=list[UserRolePublic])
async def get_roles_for_user(user_id: UUID, session: Session = Depends(get_db_session)):
    """Get all roles for a user"""
    user = session.exec(select(User).where(User.id == user_id)
        .options(
            selectinload(User.user_roles).selectinload(UserRole.role),
            selectinload(User.user_roles).selectinload(UserRole.proficiency_level)
        )).one_or_none()
    raise_exception_if_not_found(user, User, status.HTTP_404_NOT_FOUND)
    return [
        UserRolePublic.from_objects(
            user_role=ur, user=user, role=ur.role, proficiency_level=ur.proficiency_level
        ) for ur in user.user_roles
    ]

@router.get("/roles/{role_id}/users", response_model=list[UserRolePublic])
async def get_users_for_role(role_id: UUID, session: Session = Depends(get_db_session)):
    """Get all users for a role"""
    role = session.exec(select(Role).where(Role.id == role_id)
        .options(
            selectinload(Role.user_roles).selectinload(UserRole.user),
            selectinload(Role.user_roles).selectinload(UserRole.proficiency_level)
        )).one_or_none()
    raise_exception_if_not_found(role, Role, status.HTTP_404_NOT_FOUND)
    return [
        UserRolePublic.from_objects(
            user_role=ur, user=ur.user, role=role, proficiency_level=ur.proficiency_level
        ) for ur in role.user_roles
    ]

# User roles are not created or deleted directly through an API endpoint - they are created when a user or role is created (same with delete)

@router.patch("/users/{user_id}/roles/{role_id}", response_model=UserRolePublic)
async def update_user_role(user_id: UUID, role_id: UUID, payload: UserRoleUpdate, session: Session = Depends(get_db_session)):
    """Update a user role by user ID and role ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    user_role = session.exec(select(UserRole).where(UserRole.user_id == user_id).where(UserRole.role_id == role_id)).one_or_none()
    raise_exception_if_not_found(user_role, UserRole)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(user_role, key, value)
    try:
        # no need to add the user role again, it's already in the session from raise_exception_if_not_found
        session.commit()
        session.refresh(user_role)
        return UserRolePublic.from_objects(user_role=user_role, user=user_role.user, role=user_role.role, proficiency_level=user_role.proficiency_level)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e