from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import Event, EventCreate, EventUpdate, EventPublic, Schedule
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.utils.helpers import maybe

router = APIRouter()

@router.get("/schedules/{schedule_id}/events", response_model=list[EventPublic])
async def get_events(schedule_id: UUID, session: Session = Depends(get_db_session)):
    """Get all events for a schedule"""
    schedule = session.exec(
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(
            selectinload(Schedule.events).selectinload(Event.team),
            selectinload(Schedule.events).selectinload(Event.event_type),
        )
    ).one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    events_public = []
    for event in schedule.events:
        team = event.team
        events_public.append(
            EventPublic(
                id=event.id,
                schedule_id=schedule.id,
                title=event.title,
                starts_at=event.starts_at,
                ends_at=event.ends_at,
                team_id=event.team_id,
                event_type_id=event.event_type_id,
                notes=event.notes,
                is_active=event.is_active,
                schedule_month=schedule.month,
                schedule_year=schedule.year,
                schedule_notes=schedule.notes,
                schedule_is_active=schedule.is_active,
                team_name=maybe(team, "name"),
                team_code=maybe(team, "code"),
                team_is_active=maybe(team, "is_active"),
                event_type_name=event.event_type.name,
                event_type_code=event.event_type.code,
                event_type_is_active=event.event_type.is_active,
            )
        )
    return events_public

@router.get("/events/{event_id}", response_model=EventPublic)
async def get_event(event_id: UUID, session: Session = Depends(get_db_session)):
    """Get a single event"""
    event = session.exec(
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.schedule),
            selectinload(Event.team),
            selectinload(Event.event_type),
        )
    ).one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    schedule = event.schedule
    team = event.team
    event_type = event.event_type

    return EventPublic(
        id=event.id,
        schedule_id=schedule.id,
        title=event.title,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        team_id=event.team_id,
        event_type_id=event.event_type_id,
        notes=event.notes,
        is_active=event.is_active,
        schedule_month=schedule.month,
        schedule_year=schedule.year,
        schedule_notes=schedule.notes,
        schedule_is_active=schedule.is_active,
        team_name=maybe(team, "name"),
        team_code=maybe(team, "code"),
        team_is_active=maybe(team, "is_active"),
        event_type_name=event_type.name,
        event_type_code=event_type.code,
        event_type_is_active=event_type.is_active,
    )
    
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