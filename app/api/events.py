from fastapi import APIRouter, status, Response, Depends

from app.db.models import EventCreate, EventUpdate, EventPublic, EventWithAssignmentsPublic
from app.utils.dependencies import SessionDep, ScheduleForEventsDep, EventDep, EventWithFullHierarchyDep, require_admin, verify_api_key, get_optional_bearer_token, get_db_session
from app.services.builders import build_events_with_assignments_from_schedule, build_events_with_assignments_from_event
from app.services.domain import update_object, create_event_with_default_assignment_slots, delete_object

router = APIRouter(
    tags=["events"], 
    dependencies=[Depends(verify_api_key), Depends(get_optional_bearer_token), Depends(get_db_session)]
)

@router.get("/schedules/{schedule_id}/events", response_model=list[EventWithAssignmentsPublic])
def get_events_for_schedule(schedule: ScheduleForEventsDep):
    return build_events_with_assignments_from_schedule(schedule)

@router.get("/events/{id}", response_model=EventWithAssignmentsPublic)
def get_single_event(event: EventWithFullHierarchyDep):
    return build_events_with_assignments_from_event(event)

@router.post("/schedules/{schedule_id}/events", response_model=EventWithAssignmentsPublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_event(schedule: ScheduleForEventsDep, event: EventCreate, session: SessionDep):
    """Create a new event for a schedule with event assignment slots for active roles"""
    new_event = create_event_with_default_assignment_slots(session, event, schedule)
    return build_events_with_assignments_from_event(new_event)

@router.patch("/events/{id}", response_model=EventPublic, dependencies=[Depends(require_admin)])
def patch_event(payload: EventUpdate, session: SessionDep, event: EventDep):
    updated_event = update_object(session, payload, event)
    return EventPublic.from_objects(event=updated_event, schedule=updated_event.schedule, event_type=updated_event.event_type, team=updated_event.team)

@router.delete("/events/{id}", dependencies=[Depends(require_admin)])
def delete_event(session: SessionDep, event: EventDep):
    delete_object(session, event)
    return Response(status_code=status.HTTP_204_NO_CONTENT)