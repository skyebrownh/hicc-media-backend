from fastapi import APIRouter, Depends

from app.db.models import EventAssignmentUpdate, EventAssignmentPublic
from app.utils.dependencies import SessionDep, EventWithFullHierarchyForAssignmentsDep, EventAssignmentDep, require_admin, verify_api_key, get_optional_bearer_token, get_db_session
from app.services.domain import get_event_assignments_from_event, update_event_assignment

router = APIRouter(
    tags=["event_assignments"], 
    dependencies=[Depends(verify_api_key), Depends(get_optional_bearer_token), Depends(get_db_session)]
)

# Event Assignments are inserted when a new event is created - no direct route
# Event Assignments are cascade deleted when the event is deleted - no direct route

@router.get("/events/{event_id}/assignments", response_model=list[EventAssignmentPublic])
def get_assignments_by_event(event: EventWithFullHierarchyForAssignmentsDep):
    return get_event_assignments_from_event(event)

@router.patch("/assignments/{id}", response_model=EventAssignmentPublic, dependencies=[Depends(require_admin)])
def patch_event_assignment(payload: EventAssignmentUpdate, session: SessionDep, event_assignment: EventAssignmentDep):
    return update_event_assignment(session, payload, event_assignment)