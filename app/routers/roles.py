from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from sqlmodel import Session, select
from app.db.models import Role, RoleCreate, RoleUpdate
from app.utils.dependencies import get_db_session

router = APIRouter(prefix="/roles")

@router.get("", response_model=list[Role])
async def get_roles(session: Session = Depends(get_db_session)):
    return session.exec(select(Role)).all()

# @router.get("/{role_id}", response_model=MediaRoleOut)
# async def get_role(role_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await fetch_one(conn, table="roles", filters={"role_id": role_id})

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

# @router.delete("/{role_id}", response_model=MediaRoleOut)
# async def delete_role(role_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await delete_one(conn, table="roles", filters={"role_id": role_id})
