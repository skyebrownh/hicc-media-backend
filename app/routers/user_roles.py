from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import UserRole, UserRoleCreate, UserRoleUpdate, UserRolePublic, User, Role, ProficiencyLevel
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session

router = APIRouter()

@router.get("/users/{user_id}/roles", response_model=list[UserRolePublic])
async def get_roles_for_user(user_id: UUID, session: Session = Depends(get_db_session)):
    """Get all roles for a user"""
    user = session.exec(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.user_roles).selectinload(UserRole.role),
            selectinload(User.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).one_or_none()
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
    role = session.exec(
        select(Role)
        .where(Role.id == role_id)
        .options(
            selectinload(Role.user_roles).selectinload(UserRole.user),
            selectinload(Role.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).one_or_none()
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

# # Insert all roles for a user
# @router.post("/users/{user_id}/roles", response_model=list[UserRoleOut], status_code=status.HTTP_201_CREATED)
# async def post_roles_for_user(user_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     await fetch_one(conn, table="users", filters={"user_id": user_id})
#     return await insert_all_roles_for_user(conn, user_id=user_id)

# # Insert all users for a role
# @router.post("/roles/{role_id}/users", response_model=list[UserRoleOut], status_code=status.HTTP_201_CREATED)
# async def post_users_for_role(role_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     await fetch_one(conn, table="media_roles", filters={"media_role_id": role_id})
#     return await insert_all_users_for_role(conn, role_id=role_id)

# # Insert new user role
# @router.post("/user_roles", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
# async def post_user_role(user_role: UserRoleCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_user_role(conn, user_role=user_role)

# # Update a user role
# @router.patch("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
# async def patch_user_role(user_id: UUID, role_id: UUID, user_role_update: UserRoleUpdate | None = Body(default=None), conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await update_user_role(conn, user_id=user_id, role_id=role_id, payload=user_role_update)

# # Delete a user role
# @router.delete("/users/{user_id}/roles/{role_id}", response_model=UserRoleOut)
# async def delete_user_role(user_id: UUID, role_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="user_roles", filters={"user_id": user_id, "media_role_id": role_id})