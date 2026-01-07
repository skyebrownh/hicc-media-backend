from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import EventType, EventTypeCreate, EventTypeUpdate
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_raise_exception

router = APIRouter(prefix="/event_types")

@router.get("", response_model=list[EventType])
async def get_all_event_types(session: Session = Depends(get_db_session)):
    """Get all event types"""
    return session.exec(select(EventType)).all()

@router.get("/{id}", response_model=EventType)
async def get_single_event_type(id: UUID, session: Session = Depends(get_db_session)):
    """Get an event type by ID"""
    return get_or_raise_exception(session, EventType, id)

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

# @router.patch("/{event_type_id}", response_model=ScheduleDateTypeOut)
# async def patch_event_type(
#     event_type_id: UUID,
#     event_type_update: ScheduleDateTypeUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_event_type(conn, event_type_id=event_type_id, payload=event_type_update)

@router.delete("/{id}")
async def delete_event_type(id: UUID, session: Session = Depends(get_db_session)):
    """Delete an event type by ID"""
    event_type = get_or_raise_exception(session, EventType, id, status.HTTP_204_NO_CONTENT) # Event type not found, nothing to delete
    session.delete(event_type)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Event type deleted successfully