from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import EventAssignment, EventAssignmentCreate, EventAssignmentUpdate, EventAssignmentPublic, Event, User, UserRole
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.utils.helpers import maybe

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
    team = event.team
    event_type = event.event_type
    for ea in event.event_assignments:
        assigned_user = ea.assigned_user
        role = ea.role
        proficiency_level = None
        if assigned_user:
            proficiency_level = next((ur.proficiency_level for ur in assigned_user.user_roles if ur.role_id == ea.role_id), None)
        
        event_assignments_public.append(
            EventAssignmentPublic(
                id=ea.id,
                event_id=event.id,
                role_id=role.id,
                event_title=event.title,
                event_starts_at=event.starts_at,
                event_ends_at=event.ends_at,
                event_notes=event.notes,
                event_is_active=event.is_active,
                event_schedule_id=event.schedule_id,
                event_schedule_month=event.schedule.month,
                event_schedule_year=event.schedule.year,
                event_schedule_notes=event.schedule.notes,
                event_schedule_is_active=event.schedule.is_active,
                event_team_id=maybe(team, "id"),
                event_team_name=maybe(team, "name"),
                event_team_code=maybe(team, "code"),
                event_team_is_active=maybe(team, "is_active"),
                event_type_id=event_type.id,
                event_type_name=event_type.name,
                event_type_code=event_type.code,
                event_type_is_active=event_type.is_active,
                role_name=role.name,
                role_description=role.description,
                role_order=role.order,
                role_code=role.code,
                role_is_active=role.is_active,
                assigned_user_id=maybe(assigned_user, "id"),
                assigned_user_first_name=maybe(assigned_user, "first_name"),
                assigned_user_last_name=maybe(assigned_user, "last_name"),
                assigned_user_email=maybe(assigned_user, "email"),
                assigned_user_phone=maybe(assigned_user, "phone"),
                assigned_user_is_active=maybe(assigned_user, "is_active"),
                proficiency_level_id=maybe(proficiency_level, "id"),
                proficiency_level_name=maybe(proficiency_level, "name"),
                proficiency_level_rank=maybe(proficiency_level, "rank"),
                proficiency_level_is_assignable=maybe(proficiency_level, "is_assignable"),
                proficiency_level_is_active=maybe(proficiency_level, "is_active"),
                proficiency_level_code=maybe(proficiency_level, "code"),
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