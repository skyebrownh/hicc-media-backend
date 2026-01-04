from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import Event, EventCreate, EventUpdate, EventPublic, EventWithAssignmentsPublic, EventAssignmentEmbeddedPublic, EventAssignment, Schedule
from sqlmodel import Session
from app.utils.dependencies import get_db_session
from app.services.scheduling import get_event, get_schedule

router = APIRouter()

@router.get("/schedules/{schedule_id}/events", response_model=list[EventWithAssignmentsPublic])
async def get_events_for_schedule(schedule_id: UUID, session: Session = Depends(get_db_session)):
    """Get all events for a schedule"""
    schedule = get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    events_with_assignments_public = []
    for event in schedule.events:
        events_with_assignments_public.append(
            EventWithAssignmentsPublic(
                event=EventPublic.from_objects(
                    event=event,
                    schedule=schedule,
                    event_type=event.event_type,
                    team=event.team,
                ),
                event_assignments=[
                    EventAssignmentEmbeddedPublic.from_objects(
                        event_assignment=ea,
                        role=ea.role,
                        assigned_user=ea.assigned_user,
                    ) for ea in event.event_assignments
                ],
            )
        )
    return events_with_assignments_public

@router.get("/events/{event_id}", response_model=EventWithAssignmentsPublic)
async def get_single_event(event_id: UUID, session: Session = Depends(get_db_session)):
    """Get a single event"""
    event = get_event(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    return EventWithAssignmentsPublic(
        event=EventPublic.from_objects(
            event=event,
            schedule=event.schedule,
            event_type=event.event_type,
            team=event.team,
        ),
        event_assignments=[
            EventAssignmentEmbeddedPublic.from_objects(
                event_assignment=ea,
                role=ea.role,
                assigned_user=ea.assigned_user,
            ) for ea in event.event_assignments
        ],
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