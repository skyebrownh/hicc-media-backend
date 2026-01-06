from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, Response
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.db.models import Role, RoleCreate, RoleUpdate
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_404

router = APIRouter(prefix="/roles")

@router.get("", response_model=list[Role])
async def get_all_roles(session: Session = Depends(get_db_session)):
    """Get all roles"""
    return session.exec(select(Role)).all()

@router.get("/{id}", response_model=Role)
async def get_single_role(id: UUID, session: Session = Depends(get_db_session)):
    """Get a role by ID"""
    return get_or_404(session, Role, id)

# @router.post("", response_model=MediaRoleOut, status_code=status.HTTP_201_CREATED)
# async def post_role(role: MediaRoleCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await insert_role(conn, role=role)

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
    role = session.exec(
        select(Role)
        .where(Role.id == id)
        .options(selectinload(Role.user_roles)) # Ensure the relationship is loaded for cascade delete
    ).first()
    if not role:
        return Response(status_code=status.HTTP_204_NO_CONTENT) # Role not found, nothing to delete
    session.delete(role)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Role deleted successfully
