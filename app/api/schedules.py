from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic, EventWithAssignmentsAndAvailabilityPublic, EventPublic, EventAssignmentEmbeddedPublic, UserUnavailablePeriodEmbeddedPublic
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
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

@router.post("", response_model=Schedule, status_code=status.HTTP_201_CREATED)
async def post_schedule(schedule: ScheduleCreate, session: Session = Depends(get_db_session)):
    """Create a new schedule"""
    new_schedule = Schedule.model_validate(schedule)
    try:
        session.add(new_schedule)
        session.commit()
        session.refresh(new_schedule)
        return new_schedule
    except IntegrityError as e:
        session.rollback()
        if "schedule_check_month" in str(e):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid month") from e
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    
# TODO: Generate events for a schedule - using a service

# @router.patch("/{schedule_id}", response_model=ScheduleOut)
# async def patch_schedule(
#     schedule_id: UUID,
#     schedule_update: ScheduleUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_schedule(conn, schedule_id=schedule_id, payload=schedule_update)

@router.delete("/{id}")
async def delete_schedule(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a schedule by ID"""
    schedule = session.exec(
        select(Schedule)
        .where(Schedule.id == id)
        .options(selectinload(Schedule.events)) # Ensure the relationship is loaded for cascade delete
    ).first()
    if not schedule:
        return Response(status_code=status.HTTP_204_NO_CONTENT) # Schedule not found, nothing to delete
    session.delete(schedule)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Schedule deleted successfully