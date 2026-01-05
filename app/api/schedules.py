from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic, EventWithAssignmentsAndAvailabilityPublic, EventPublic, EventAssignmentEmbeddedPublic, UserUnavailablePeriodEmbeddedPublic
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_404
from app.services.queries import get_schedule, get_unavailable_users_for_event

router = APIRouter(prefix="/schedules")

@router.get("", response_model=list[Schedule])
async def get_all_schedules(session: Session = Depends(get_db_session)):
    """Get all schedules"""
    return session.exec(select(Schedule)).all()

@router.get("/{id}", response_model=Schedule)
async def get_single_schedule(id: UUID, session: Session = Depends(get_db_session)):
    """Get a schedule by ID"""
    return get_or_404(session, Schedule, id)

@router.get("/{id}/grid", response_model=ScheduleGridPublic)
async def get_schedule_grid(id: UUID, session: Session = Depends(get_db_session)):
    """Get a schedule grid by ID"""
    schedule = get_schedule(session, id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    schedule_grid_events = []
    for event in schedule.events:
        unavailable_users = get_unavailable_users_for_event(session=session, event_id=event.id)
        unavailable_users = [] if unavailable_users is None else unavailable_users
        schedule_grid_events.append(
            EventWithAssignmentsAndAvailabilityPublic(
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
                availability=[
                    UserUnavailablePeriodEmbeddedPublic(
                        user_first_name=ua.user.first_name,
                        user_last_name=ua.user.last_name
                    ) for ua in unavailable_users
                ],
            )
        )
    return ScheduleGridPublic.from_objects(schedule=schedule, events=schedule_grid_events)

# @router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
# async def post_schedule(schedule: ScheduleCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_schedule(conn, schedule=schedule)
    
# # TODO: Insert schedule dates for a schedule based on configuration

# @router.patch("/{schedule_id}", response_model=ScheduleOut)
# async def patch_schedule(
#     schedule_id: UUID,
#     schedule_update: ScheduleUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_schedule(conn, schedule_id=schedule_id, payload=schedule_update)

# @router.delete("/{schedule_id}", response_model=ScheduleOut)
# async def delete_schedule(schedule_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="schedules", filters={"schedule_id": schedule_id})
    
# @router.delete("/{schedule_id}/schedule_dates", response_model=list[ScheduleDateOut])
# async def delete_schedule_dates_for_schedule(schedule_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     # Verify schedule exists first (will raise 404 if not found)
#     await fetch_one(conn, table="schedules", filters={"schedule_id": schedule_id})
#     return await delete_all(conn, table="schedule_dates", filters={"schedule_id": schedule_id})