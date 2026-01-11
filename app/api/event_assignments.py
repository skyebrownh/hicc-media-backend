from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models import EventAssignment, EventAssignmentUpdate, EventAssignmentPublic, Event
from sqlmodel import Session
from app.utils.dependencies import get_db_session
from app.services.queries import select_event_with_full_hierarchy, select_full_event_assignment
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter()

# Event Assignments are inserted when a new event is created - no direct route
# Event Assignments are cascade deleted when the event is deleted - no direct route

@router.get("/events/{event_id}/assignments", response_model=list[EventAssignmentPublic])
async def get_event_assignments_by_event(event_id: UUID, session: Session = Depends(get_db_session)):
    """Get all event assignments for an event"""
    event = select_event_with_full_hierarchy(session, event_id)
    raise_exception_if_not_found(event, Event, status.HTTP_404_NOT_FOUND)
    event_assignments_public = []
    for ea in event.event_assignments:
        assigned_user = ea.assigned_user
        proficiency_level = None
        if assigned_user:
            proficiency_level = next((ur.proficiency_level for ur in assigned_user.user_roles if ur.role_id == ea.role_id), None)
        
        event_assignments_public.append(
            EventAssignmentPublic.from_objects(
                event_assignment=ea,
                event=event,
                role=ea.role,
                event_type=event.event_type,
                team=event.team,
                assigned_user=assigned_user,
                proficiency_level=proficiency_level,
            )
        )
    return event_assignments_public

@router.patch("/assignments/{id}", response_model=EventAssignmentPublic)
async def update_event_assignment(id: UUID, payload: EventAssignmentUpdate, session: Session = Depends(get_db_session)):
    """Update a event assignment by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    event_assignment = select_full_event_assignment(session, id)
    raise_exception_if_not_found(event_assignment, EventAssignment)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(event_assignment, key, value)
    try:
        # no need to add the event assignment again, it's already in the session from get_event_assignment
        session.commit()
        session.refresh(event_assignment)
        proficiency_level = next((ur.proficiency_level for ur in event_assignment.assigned_user.user_roles if ur.role_id == event_assignment.role_id), None)
        return EventAssignmentPublic.from_objects(
            event_assignment=event_assignment,
            event=event_assignment.event,
            role=event_assignment.role,
            event_type=event_assignment.event.event_type,
            team=event_assignment.event.team,
            assigned_user=event_assignment.assigned_user,
            proficiency_level=proficiency_level
        )
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e