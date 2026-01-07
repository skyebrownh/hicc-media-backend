from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.db.models import Role, RoleCreate, RoleUpdate, User, UserRole, ProficiencyLevel
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_raise_exception, raise_exception_if_not_found
from app.services.queries import get_role

router = APIRouter(prefix="/roles")

@router.get("", response_model=list[Role])
async def get_all_roles(session: Session = Depends(get_db_session)):
    """Get all roles"""
    return session.exec(select(Role)).all()

@router.get("/{id}", response_model=Role)
async def get_single_role(id: UUID, session: Session = Depends(get_db_session)):
    """Get a role by ID"""
    return get_or_raise_exception(session, Role, id)

@router.post("", response_model=Role, status_code=status.HTTP_201_CREATED)
async def post_role(role: RoleCreate, session: Session = Depends(get_db_session)):
    """Create a new role"""
    new_role = Role.model_validate(role)
    try:
        session.add(new_role)
        session.flush()  # Flush to get the ID before creating UserRole records

        # Create user_roles for this new role for every user
        untrained_proficiency_level = session.exec(select(ProficiencyLevel).where(ProficiencyLevel.name == "Untrained")).first()
        proficiency_level_id = untrained_proficiency_level.id if untrained_proficiency_level else None
        for user in session.exec(select(User)).all():
            session.add(UserRole(user_id=user.id, role_id=new_role.id, proficiency_level_id=proficiency_level_id))

        session.commit()
        session.refresh(new_role)
        return new_role
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

# @router.patch("/{role_id}", response_model=MediaRoleOut)
# async def patch_role(
#     role_id: UUID,
#     role_update: MediaRoleUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#         return await update_role(conn, role_id=role_id, payload=role_update)

@router.delete("/{id}")
async def delete_role(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a role by ID"""
    role = get_role(session, id)
    raise_exception_if_not_found(role, Role, status.HTTP_204_NO_CONTENT) # Role not found, nothing to delete
    session.delete(role)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Role deleted successfully
