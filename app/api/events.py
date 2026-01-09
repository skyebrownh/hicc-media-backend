from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import Event, EventCreate, EventUpdate, EventPublic, EventWithAssignmentsPublic, Schedule, Role, EventAssignment
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.services.queries import get_event, get_schedule_only, get_event_for_cascade_delete
from app.utils.helpers import build_events_with_assignments_from_schedule, build_events_with_assignments_from_event, raise_exception_if_not_found

router = APIRouter()

@router.get("/schedules/{schedule_id}/events", response_model=list[EventWithAssignmentsPublic])
async def get_events_for_schedule(schedule_id: UUID, session: Session = Depends(get_db_session)):
    """Get all events for a schedule"""
    schedule = get_schedule_only(session, schedule_id)
    raise_exception_if_not_found(schedule, Schedule, status.HTTP_404_NOT_FOUND)
    return build_events_with_assignments_from_schedule(schedule)

@router.get("/events/{id}", response_model=EventWithAssignmentsPublic)
async def get_single_event(id: UUID, session: Session = Depends(get_db_session)):
    """Get a single event"""
    event = get_event(session, id)
    raise_exception_if_not_found(event, Event, status.HTTP_404_NOT_FOUND)
    return build_events_with_assignments_from_event(event)

@router.post("/schedules/{schedule_id}/events", response_model=EventWithAssignmentsPublic, status_code=status.HTTP_201_CREATED)
async def post_event(schedule_id: UUID, event: EventCreate, session: Session = Depends(get_db_session)):
    """Create a new event for a schedule with event assignment slots for active roles"""
    schedule = get_schedule_only(session, schedule_id)
    raise_exception_if_not_found(schedule, Schedule, status.HTTP_404_NOT_FOUND)
    new_event = Event(schedule_id=schedule_id, **event.model_dump())

    active_roles = session.exec(select(Role).where(Role.is_active == True)).all()
    for role in active_roles:
        # TODO: Set is_applicable and requirement_level
        new_event.event_assignments.append(EventAssignment(event_id=new_event.id, role_id=role.id))

    try:
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        return build_events_with_assignments_from_event(new_event)
    except IntegrityError as e:
        session.rollback()
        if "event_check_time_range" in str(e):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Start time must be before end time") from e
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

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