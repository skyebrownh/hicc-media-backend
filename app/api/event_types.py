from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.db.models import EventType, EventTypeCreate, EventTypeUpdate
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_404

router = APIRouter(prefix="/event_types")

@router.get("", response_model=list[EventType])
async def get_all_event_types(session: Session = Depends(get_db_session)):
    """Get all event types"""
    return session.exec(select(EventType)).all()

@router.get("/{id}", response_model=EventType)
async def get_single_event_type(id: UUID, session: Session = Depends(get_db_session)):
    """Get an event type by ID"""
    return get_or_404(session, EventType, id)

# @router.post("", response_model=ScheduleDateTypeOut, status_code=status.HTTP_201_CREATED)
# async def post_event_type(event_type: ScheduleDateTypeCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_event_type(conn, event_type=event_type)

# @router.patch("/{event_type_id}", response_model=ScheduleDateTypeOut)
# async def patch_event_type(
#     event_type_id: UUID,
#     event_type_update: ScheduleDateTypeUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_event_type(conn, event_type_id=event_type_id, payload=event_type_update)

# @router.delete("/{event_type_id}", response_model=ScheduleDateTypeOut)
# async def delete_event_type(event_type_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="event_types", filters={"event_type_id": event_type_id})