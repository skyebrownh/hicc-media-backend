from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import User, UserCreate, UserUpdate, Role, UserRole, ProficiencyLevel
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_raise_exception, raise_exception_if_not_found
from app.services.queries import get_user

router = APIRouter(prefix="/users")

@router.get("", response_model=list[User])
async def get_all_users(session: Session = Depends(get_db_session)):
    """Get all users"""
    return session.exec(select(User)).all()

@router.get("/{id}", response_model=User)
async def get_single_user(id: UUID, session: Session = Depends(get_db_session)):
    """Get a user by ID"""
    return get_or_raise_exception(session, User, id)

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def post_user(user: UserCreate, session: Session = Depends(get_db_session)):
    """Create a new user"""
    new_user = User.model_validate(user)
    try:
        session.add(new_user)
        session.flush()  # Flush to get the ID before creating UserRole records

        # Create user_roles for this new user for every role
        untrained_proficiency_level = session.exec(select(ProficiencyLevel).where(ProficiencyLevel.name == "Untrained")).first()
        proficiency_level_id = untrained_proficiency_level.id if untrained_proficiency_level else None
        for role in session.exec(select(Role)).all():
            session.add(UserRole(user_id=new_user.id, role_id=role.id, proficiency_level_id=proficiency_level_id))

        session.commit()
        session.refresh(new_user)
        return new_user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

# @router.patch("/{user_id}", response_model=UserOut)
# async def patch_user(
#     user_id: UUID,
#     user_update: UserUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_user(conn, user_id=user_id, payload=user_update)

@router.delete("/{id}")
async def delete_user(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a user by ID"""
    user = get_user(session, id)
    raise_exception_if_not_found(user, User, status.HTTP_204_NO_CONTENT) # User not found, nothing to delete
    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # User deleted successfully