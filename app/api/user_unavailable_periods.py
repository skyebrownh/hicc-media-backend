from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from app.db.models import UserUnavailablePeriod, UserUnavailablePeriodCreate, UserUnavailablePeriodUpdate, UserUnavailablePeriodPublic, User
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_raise_exception, raise_exception_if_not_found
from app.services.queries import get_user

router = APIRouter()

@router.post("/users/{user_id}/availability", response_model=UserUnavailablePeriodPublic, status_code=status.HTTP_201_CREATED)
async def post_user_unavailable_period(user_id: UUID, payload: UserUnavailablePeriodCreate, session: Session = Depends(get_db_session)):
    """Create a new user unavailable period"""
    user = get_user(session, user_id)
    raise_exception_if_not_found(user, User)
    new_user_unavailable_period = UserUnavailablePeriod(user_id=user_id, starts_at=payload.starts_at, ends_at=payload.ends_at)
    try:
        session.add(new_user_unavailable_period)
        session.commit()
        session.refresh(new_user_unavailable_period)
        return UserUnavailablePeriodPublic(
            id=new_user_unavailable_period.id,
            user_id=new_user_unavailable_period.user_id,
            starts_at=new_user_unavailable_period.starts_at,
            ends_at=new_user_unavailable_period.ends_at,
            user_first_name=new_user_unavailable_period.user.first_name,
            user_last_name=new_user_unavailable_period.user.last_name,
            user_email=new_user_unavailable_period.user.email,
            user_phone=new_user_unavailable_period.user.phone,
            user_is_active=new_user_unavailable_period.user.is_active,
        )
    except IntegrityError as e:
        session.rollback()
        if "user_unavailable_period_check_time_range" in str(e):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Start time must be before end time") from e
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.post("/users/{user_id}/availability/bulk", response_model=list[UserUnavailablePeriodPublic], status_code=status.HTTP_201_CREATED)
async def post_user_unavailable_periods_bulk(user_id: UUID, payload: list[UserUnavailablePeriodCreate], session: Session = Depends(get_db_session)):
    """Create new user unavailable periods in bulk"""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload cannot be empty")
    user = get_user(session, user_id)
    raise_exception_if_not_found(user, User)
    bulk_periods = [UserUnavailablePeriod(user_id=user_id, starts_at=period.starts_at, ends_at=period.ends_at) for period in payload]
    period_ids = [period.id for period in bulk_periods]
    try:
        session.add_all(bulk_periods)
        session.commit()
        # re-fetch to refresh the objects
        refreshed_periods = session.exec(
            select(UserUnavailablePeriod)
            .where(UserUnavailablePeriod.id.in_(period_ids))
            .options(selectinload(UserUnavailablePeriod.user))
        ).all()
        # build public models
        public_periods = [
            UserUnavailablePeriodPublic(
                id=period.id,
                user_id=period.user_id,
                starts_at=period.starts_at,
                ends_at=period.ends_at,
                user_first_name=period.user.first_name,
                user_last_name=period.user.last_name,
                user_email=period.user.email,
                user_phone=period.user.phone,
                user_is_active=period.user.is_active,
            )
            for period in refreshed_periods
        ]
        return public_periods
    except IntegrityError as e:
        session.rollback()
        if "user_unavailable_period_check_time_range" in str(e):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Start time must be before end time") from e
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.patch("/user_availability/{id}", response_model=UserUnavailablePeriodPublic)
async def update_user_unavailable_period(id: UUID, payload: UserUnavailablePeriodUpdate, session: Session = Depends(get_db_session)):
    """Update a user unavailable period by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    user_unavailable_period = get_or_raise_exception(session, UserUnavailablePeriod, id)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(user_unavailable_period, key, value)
    try:
        # no need to add the user unavailable period again, it's already in the session from get_or_raise_exception
        session.commit()
        session.refresh(user_unavailable_period)
        return UserUnavailablePeriodPublic(
            id=user_unavailable_period.id,
            user_id=user_unavailable_period.user_id,
            starts_at=user_unavailable_period.starts_at,
            ends_at=user_unavailable_period.ends_at,
            user_first_name=user_unavailable_period.user.first_name,
            user_last_name=user_unavailable_period.user.last_name,
            user_email=user_unavailable_period.user.email,
            user_phone=user_unavailable_period.user.phone,
            user_is_active=user_unavailable_period.user.is_active,
        )
    except IntegrityError as e:
        session.rollback()
        if "user_unavailable_period_check_time_range" in str(e):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Start time must be before end time") from e
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/user_availability/{id}")
async def delete_user_unavailable_period(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a user unavailable period by ID"""
    user_unavailable_period = get_or_raise_exception(session, UserUnavailablePeriod, id, status.HTTP_204_NO_CONTENT) # User unavailable period not found, nothing to delete
    session.delete(user_unavailable_period)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # User unavailable period deleted successfully