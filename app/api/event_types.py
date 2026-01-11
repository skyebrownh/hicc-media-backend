from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import EventType, EventTypeCreate, EventTypeUpdate
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter(prefix="/event_types")

@router.get("", response_model=list[EventType])
async def get_all_event_types(session: Session = Depends(get_db_session)):
    """Get all event types"""
    return session.exec(select(EventType)).all()

@router.get("/{id}", response_model=EventType)
async def get_single_event_type(id: UUID, session: Session = Depends(get_db_session)):
    """Get an event type by ID"""
    event_type = session.get(EventType, id)
    raise_exception_if_not_found(event_type, EventType)
    return event_type

@router.post("", response_model=EventType, status_code=status.HTTP_201_CREATED)
async def post_event_type(event_type: EventTypeCreate, session: Session = Depends(get_db_session)):
    """Create a new event type"""
    new_event_type = EventType.model_validate(event_type)
    try:
        session.add(new_event_type)
        session.commit()
        session.refresh(new_event_type)
        return new_event_type
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.patch("/{id}", response_model=EventType)
async def update_event_type(id: UUID, payload: EventTypeUpdate, session: Session = Depends(get_db_session)):
    """Update an event type by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    event_type = session.get(EventType, id)
    raise_exception_if_not_found(event_type, EventType)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(event_type, key, value)
    try:
        # no need to add the event type again, it's already in the session from get_or_raise_exception
        session.commit()
        session.refresh(event_type)
        return event_type
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/{id}")
async def delete_event_type(id: UUID, session: Session = Depends(get_db_session)):
    """Delete an event type by ID"""
    event_type = session.get(EventType, id)
    raise_exception_if_not_found(event_type, EventType, status.HTTP_204_NO_CONTENT) # Event type not found, nothing to delete
    session.delete(event_type)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Event type deleted successfully