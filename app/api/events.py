from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import Event, EventCreate, EventUpdate, EventPublic, EventWithAssignmentsPublic, Schedule, Role, EventAssignment
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.services.queries import select_event_with_full_hierarchy
from app.utils.helpers import build_events_with_assignments_from_schedule, build_events_with_assignments_from_event, raise_exception_if_not_found

router = APIRouter()

@router.get("/schedules/{schedule_id}/events", response_model=list[EventWithAssignmentsPublic])
async def get_events_for_schedule(schedule_id: UUID, session: Session = Depends(get_db_session)):
    """Get all events for a schedule"""
    schedule = session.exec(select(Schedule).where(Schedule.id == schedule_id)).one_or_none()
    raise_exception_if_not_found(schedule, Schedule, status.HTTP_404_NOT_FOUND)
    return build_events_with_assignments_from_schedule(schedule)

@router.get("/events/{id}", response_model=EventWithAssignmentsPublic)
async def get_single_event(id: UUID, session: Session = Depends(get_db_session)):
    """Get a single event"""
    event = select_event_with_full_hierarchy(session, id)
    raise_exception_if_not_found(event, Event, status.HTTP_404_NOT_FOUND)
    return build_events_with_assignments_from_event(event)

@router.post("/schedules/{schedule_id}/events", response_model=EventWithAssignmentsPublic, status_code=status.HTTP_201_CREATED)
async def post_event(schedule_id: UUID, event: EventCreate, session: Session = Depends(get_db_session)):
    """Create a new event for a schedule with event assignment slots for active roles"""
    schedule = session.exec(select(Schedule).where(Schedule.id == schedule_id)).one_or_none()
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

@router.patch("/events/{id}", response_model=EventPublic)
async def update_event(id: UUID, payload: EventUpdate, session: Session = Depends(get_db_session)):
    """Update an event by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    event = session.get(Event, id)
    raise_exception_if_not_found(event, Event)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(event, key, value)
    try:
        # no need to add the event again, it's already in the session from raise_exception_if_not_found
        session.commit()
        session.refresh(event)
        return EventPublic.from_objects(
            event=event, schedule=event.schedule, event_type=event.event_type, team=event.team
        )
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/events/{id}")
async def delete_event(id: UUID, session: Session = Depends(get_db_session)):
    """Delete an event by ID"""
    event = session.exec(select(Event).where(Event.id == id).options(selectinload(Event.event_assignments))).one_or_none()
    raise_exception_if_not_found(event, Event, status.HTTP_204_NO_CONTENT) # Event not found, nothing to delete
    session.delete(event)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Event deleted successfully