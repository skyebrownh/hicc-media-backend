from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.db.models import EventAssignment, EventAssignmentCreate, EventAssignmentUpdate, EventAssignmentPublic, Event
from sqlmodel import Session
from app.utils.dependencies import get_db_session
from app.services.queries import get_event
from app.utils.helpers import raise_exception_if_not_found

router = APIRouter()

@router.get("/events/{event_id}/assignments", response_model=list[EventAssignmentPublic])
async def get_event_assignments_by_event(event_id: UUID, session: Session = Depends(get_db_session)):
    """Get all event assignments for an event"""
    event = get_event(session, event_id)
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

# # Insert new event assignment
# @router.post("", response_model=ScheduleDateRoleOut, status_code=status.HTTP_201_CREATED)
# async def post_event_assignment(event_assignment: ScheduleDateRoleCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_event_assignment(conn, event_assignment=event_assignment)

# # Update event assignment
# @router.patch("/{event_assignment_id}", response_model=ScheduleDateRoleOut)
# async def patch_event_assignment(
#     event_assignment_id: UUID,
#     event_assignment_update: ScheduleDateRoleUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_event_assignment(conn, event_assignment_id=event_assignment_id, payload=event_assignment_update)