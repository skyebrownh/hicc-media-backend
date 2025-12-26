from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.db.models import EventAssignment, EventAssignmentCreate, EventAssignmentUpdate, EventAssignmentPublic, Event, User, UserRole
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.utils.helpers import maybe

router = APIRouter(prefix="/event_assignments")

# Get all event assignments
@router.get("", response_model=list[EventAssignmentPublic])
async def get_event_assignments(session: Session = Depends(get_db_session)):
    event_assignments = session.exec(
        select(EventAssignment)
        .options(
            selectinload(EventAssignment.event).selectinload(Event.schedule),
            selectinload(EventAssignment.event).selectinload(Event.team),
            selectinload(EventAssignment.event).selectinload(Event.event_type),
            selectinload(EventAssignment.role),
            selectinload(EventAssignment.assigned_user).selectinload(User.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).all()

    event_assignments_public = []
    for ea in event_assignments:
        team = ea.event.team
        assigned_user = ea.assigned_user
        proficiency_level = None
        if assigned_user:
            proficiency_level = next((ur.proficiency_level for ur in assigned_user.user_roles if ur.role_id == ea.role_id), None)
        event_assignments_public.append(
            EventAssignmentPublic(
                id=ea.id,
                event_id=ea.event_id,
                role_id=ea.role_id,
                event_title=ea.event.title,
                event_starts_at=ea.event.starts_at,
                event_ends_at=ea.event.ends_at,
                event_notes=ea.event.notes,
                event_is_active=ea.event.is_active,
                event_schedule_id=ea.event.schedule_id,
                event_schedule_month=ea.event.schedule.month,
                event_schedule_year=ea.event.schedule.year,
                event_schedule_notes=ea.event.schedule.notes,
                event_schedule_is_active=ea.event.schedule.is_active,
                event_team_id=maybe(team, "id"),
                event_team_name=maybe(team, "name"),
                event_team_code=maybe(team, "code"),
                event_team_is_active=maybe(team, "is_active"),
                event_type_id=ea.event.event_type_id,
                event_type_name=ea.event.event_type.name,
                event_type_code=ea.event.event_type.code,
                event_type_is_active=ea.event.event_type.is_active,
                role_name=ea.role.name,
                role_description=ea.role.description,
                role_order=ea.role.order,
                role_code=ea.role.code,
                role_is_active=ea.role.is_active,
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

# # Get single event assignment
# @router.get("/{event_assignment_id}", response_model=ScheduleDateRoleOut)
# async def get_event_assignment(event_assignment_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await fetch_one(conn, table="event_assignments", filters={"event_assignment_id": event_assignment_id})
    
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