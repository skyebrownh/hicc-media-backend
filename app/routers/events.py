from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.db.models import Event, EventCreate, EventUpdate, EventPublic
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.utils.helpers import maybe

router = APIRouter(prefix="/events")

# Get all events
@router.get("", response_model=list[EventPublic])
async def get_events(session: Session = Depends(get_db_session)):
    events = session.exec(
        select(Event)
        .options(
            selectinload(Event.schedule),
            selectinload(Event.team),
            selectinload(Event.event_type),
        )
    ).all()

    events_public = []
    for event in events:
        team = event.team
        events_public.append(
            EventPublic(
            id=event.id,
            schedule_id=event.schedule_id,
            title=event.title,
            starts_at=event.starts_at,
            ends_at=event.ends_at,
            team_id=event.team_id,
            event_type_id=event.event_type_id,
            notes=event.notes,
            is_active=event.is_active,
            schedule_month=event.schedule.month,
            schedule_year=event.schedule.year,
            schedule_notes=event.schedule.notes,
            schedule_is_active=event.schedule.is_active,
            team_name=maybe(team, "name"),
            team_code=maybe(team, "code"),
            team_is_active=maybe(team, "is_active"),
            event_type_name=event.event_type.name,
            event_type_code=event.event_type.code,
            event_type_is_active=event.event_type.is_active,
        )
        )

    return events_public

# # Get all event assignments for a event
# @router.get("/{event_id}/roles", response_model=list[ScheduleDateRoleOut])
# async def get_all_event_roles_by_event(event_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     await fetch_one(conn, table="events", filters={"event_id": event_id})
#     return await fetch_all(conn, table="event_roles", filters={"event_id": event_id})
    
# # Get all user unavailable periods for a event
# @router.get("/{event_id}/user_dates", response_model=list[UserDateOut])
# async def get_all_user_dates_by_event(event_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     event = await fetch_one(conn, table="events", filters={"event_id": event_id})
#     return await fetch_all(conn, table="user_dates", filters={"date": event["date"]})
    
# # Get single event
# @router.get("/{event_id}", response_model=ScheduleDateOut)
# async def get_event(event_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await fetch_one(conn, table="events", filters={"event_id": event_id})

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

# # Delete event
# @router.delete("/{event_id}", response_model=ScheduleDateOut)
# async def delete_event(event_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="events", filters={"event_id": event_id})
    
# # Delete event assignments for a event
# @router.delete("/{event_id}/roles", response_model=list[ScheduleDateRoleOut])
# async def delete_event_roles_for_event(event_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     await fetch_one(conn, table="events", filters={"event_id": event_id})
#     return await delete_all(conn, table="event_roles", filters={"event_id": event_id})