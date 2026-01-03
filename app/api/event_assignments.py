from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import EventAssignment, EventAssignmentCreate, EventAssignmentUpdate, EventAssignmentPublic, Event, User, UserRole
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session

router = APIRouter()

@router.get("/events/{event_id}/assignments", response_model=list[EventAssignmentPublic])
async def get_event_assignments(event_id: UUID, session: Session = Depends(get_db_session)):
    """Get all event assignments for an event"""
    event = session.exec(
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.schedule),
            selectinload(Event.team),
            selectinload(Event.event_type),
            selectinload(Event.event_assignments).selectinload(EventAssignment.role),
            selectinload(Event.event_assignments).selectinload(EventAssignment.assigned_user).selectinload(User.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

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
 
# # Delete event assignment
# @router.delete("/{event_assignment_id}", response_model=ScheduleDateRoleOut)
# async def delete_event_assignment(event_assignment_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="event_assignments", filters={"event_assignment_id": event_assignment_id})