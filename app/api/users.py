from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.db.models import User, UserCreate, UserUpdate
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_404

router = APIRouter(prefix="/users")

@router.get("", response_model=list[User])
async def get_all_users(session: Session = Depends(get_db_session)):
    """Get all users"""
    return session.exec(select(User)).all()

@router.get("/{id}", response_model=User)
async def get_single_user(id: UUID, session: Session = Depends(get_db_session)):
    """Get a user by ID"""
    return get_or_404(session, User, id)

# @router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
# async def post_user(user: UserCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_user(conn, user=user)

# @router.patch("/{user_id}", response_model=UserOut)
# async def patch_user(
#     user_id: UUID,
#     user_update: UserUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_user(conn, user_id=user_id, payload=user_update)

# @router.delete("/{user_id}", response_model=UserOut)
# async def delete_user(user_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="users", filters={"user_id": user_id})