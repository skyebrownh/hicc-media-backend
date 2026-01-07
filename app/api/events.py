from uuid import UUID
from fastapi import APIRouter, Depends, status, Response
from app.db.models import Event, EventCreate, EventUpdate, EventPublic, EventWithAssignmentsPublic, EventAssignmentEmbeddedPublic, Schedule
from sqlmodel import Session
from app.utils.dependencies import get_db_session
from app.services.queries import get_event, get_schedule, get_event_for_cascade_delete
from app.utils.helpers import build_events_with_assignments_from_schedule, build_events_with_assignments_from_event, raise_exception_if_not_found

router = APIRouter()

@router.get("/schedules/{schedule_id}/events", response_model=list[EventWithAssignmentsPublic])
async def get_events_for_schedule(schedule_id: UUID, session: Session = Depends(get_db_session)):
    """Get all events for a schedule"""
    schedule = get_schedule(session, schedule_id)
    raise_exception_if_not_found(schedule, Schedule, status.HTTP_404_NOT_FOUND)
    return build_events_with_assignments_from_schedule(schedule)

@router.get("/events/{id}", response_model=EventWithAssignmentsPublic)
async def get_single_event(id: UUID, session: Session = Depends(get_db_session)):
    """Get a single event"""
    event = get_event(session, id)
    raise_exception_if_not_found(event, Event, status.HTTP_404_NOT_FOUND)
    return build_events_with_assignments_from_event(event)

# # Insert new event
# @router.post("", response_model=ScheduleDateOut, status_code=status.HTTP_201_CREATED)
# async def post_event(event: ScheduleDateCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_event(conn, event=event)
    
# # TODO: Insert event roles for a event based on configuration

# # Update event
# @router.patch("/{event_id}", response_model=ScheduleDateOut)
# async def patch_event(
#     event_id: UUID,
#     event_update: ScheduleDateUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_event(conn, event_id=event_id, payload=event_update)

@router.delete("/events/{id}")
async def delete_event(id: UUID, session: Session = Depends(get_db_session)):
    """Delete an event by ID"""
    event = get_event_for_cascade_delete(session, id)
    raise_exception_if_not_found(event, Event, status.HTTP_204_NO_CONTENT) # Event not found, nothing to delete
    session.delete(event)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Event deleted successfully