from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import User, UserCreate, UserUpdate, Role, UserRole, ProficiencyLevel
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter(prefix="/users")

@router.get("", response_model=list[User])
async def get_all_users(session: Session = Depends(get_db_session)):
    """Get all users"""
    return session.exec(select(User)).all()

@router.get("/{id}", response_model=User)
async def get_single_user(id: UUID, session: Session = Depends(get_db_session)):
    """Get a user by ID"""
    user = session.get(User, id)
    raise_exception_if_not_found(user, User)
    return user

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

@router.patch("/{id}", response_model=User)
async def update_user(id: UUID, payload: UserUpdate, session: Session = Depends(get_db_session)):
    """Update a user by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    user = session.get(User, id)
    raise_exception_if_not_found(user, User)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(user, key, value)
    try:
        # no need to add the user again, it's already in the session from raise_exception_if_not_found
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/{id}")
async def delete_user(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a user by ID"""
    user = session.exec(select(User).where(User.id == id).options(selectinload(User.user_roles))).one_or_none()
    raise_exception_if_not_found(user, User, status.HTTP_204_NO_CONTENT) # User not found, nothing to delete
    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # User deleted successfully