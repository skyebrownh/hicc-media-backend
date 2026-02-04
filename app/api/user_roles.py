from fastapi import APIRouter, Depends

from app.db.models import UserRoleUpdate, UserRolePublic
from app.utils.dependencies import UserWithUserRolesDep, SessionDep, RoleWithUserRolesDep, UserRoleDep, require_admin
from app.services.domain import update_user_role

router = APIRouter(tags=["user_roles"])

# User roles are not created or deleted directly through an API endpoint - they are created when a user or role is created (same with delete)

@router.get("/users/{user_id}/roles", response_model=list[UserRolePublic])
def get_roles_for_user(user: UserWithUserRolesDep):
    return [
        UserRolePublic.from_objects(
            user_role=ur, user=user, role=ur.role, proficiency_level=ur.proficiency_level
        ) for ur in user.user_roles
    ]

@router.get("/roles/{role_id}/users", response_model=list[UserRolePublic])
def get_users_for_role(role: RoleWithUserRolesDep):
    return [
        UserRolePublic.from_objects(user_role=ur, user=ur.user, role=role, proficiency_level=ur.proficiency_level)
        for ur in role.user_roles
    ]

@router.patch("/users/{user_id}/roles/{role_id}", response_model=UserRolePublic, dependencies=[Depends(require_admin)])
def patch_user_role(payload: UserRoleUpdate, session: SessionDep, user_role: UserRoleDep):
    return update_user_role(session, payload, user_role)