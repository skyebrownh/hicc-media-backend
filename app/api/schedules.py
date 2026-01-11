from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic, EventWithAssignmentsAndAvailabilityPublic, EventPublic, EventAssignmentEmbeddedPublic, UserUnavailablePeriodEmbeddedPublic
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.utils.dependencies import get_db_session
from app.utils.helpers import raise_exception_if_not_found
from app.services.queries import select_schedule_with_events_and_assignments, select_unavailable_users_for_event

router = APIRouter(prefix="/schedules")

@router.get("", response_model=list[Schedule])
async def get_all_schedules(session: Session = Depends(get_db_session)):
    """Get all schedules"""
    return session.exec(select(Schedule)).all()

@router.get("/{id}", response_model=Schedule)
async def get_single_schedule(id: UUID, session: Session = Depends(get_db_session)):
    """Get a schedule by ID"""
    schedule = session.get(Schedule, id)
    raise_exception_if_not_found(schedule, Schedule)
    return schedule

@router.get("/{id}/grid", response_model=ScheduleGridPublic)
async def get_schedule_grid(id: UUID, session: Session = Depends(get_db_session)):
    """Get a schedule grid by ID"""
    schedule = select_schedule_with_events_and_assignments(session, id)
    raise_exception_if_not_found(schedule, Schedule, status.HTTP_404_NOT_FOUND)

    schedule_grid_events = []
    for event in schedule.events:
        unavailable_users = select_unavailable_users_for_event(session=session, event_id=event.id)
        unavailable_users = [] if unavailable_users is None else unavailable_users
        schedule_grid_events.append(
            EventWithAssignmentsAndAvailabilityPublic(
                event=EventPublic.from_objects(
                    event=event, schedule=schedule, event_type=event.event_type, team=event.team
                ),
                event_assignments=[
                    EventAssignmentEmbeddedPublic.from_objects(
                        event_assignment=ea, role=ea.role, assigned_user=ea.assigned_user,
                    ) for ea in event.event_assignments
                ],
                availability=[
                    UserUnavailablePeriodEmbeddedPublic(
                        user_first_name=ua.user.first_name, user_last_name=ua.user.last_name
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
    
# @router.post("/schedules/{schedule_id}/events/generate", response_model=list[EventPublic], status_code=status.HTTP_201_CREATED)
# async def generate_events(schedule_id: UUID, session: Session = Depends(get_db_session)):
#     """Generate events for a schedule based on query parameters (or defaults if not provided)"""
#     schedule = get_schedule_only(session, schedule_id)
#     raise_exception_if_not_found(schedule, Schedule, status.HTTP_404_NOT_FOUND)
#     # TODO: Generate events for a schedule - using a service

@router.patch("/{id}", response_model=Schedule)
async def update_schedule(id: UUID, payload: ScheduleUpdate, session: Session = Depends(get_db_session)):
    """Update a schedule by ID"""
    # Check if payload has any fields to update - not caught by Pydantic's RequestValidationError since update fields are not required
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    
    schedule = session.get(Schedule, id)
    raise_exception_if_not_found(schedule, Schedule)
    # Only update fields that were actually provided in the payload
    for key, value in payload_dict.items():
        setattr(schedule, key, value)
    try:
        # no need to add the schedule again, it's already in the session from raise_exception_if_not_found
        session.commit()
        session.refresh(schedule)
        return schedule
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

@router.delete("/{id}")
async def delete_schedule(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a schedule by ID"""
    schedule = session.exec(select(Schedule).where(Schedule.id == id).options(selectinload(Schedule.events))).one_or_none()
    raise_exception_if_not_found(schedule, Schedule, status.HTTP_204_NO_CONTENT) # Schedule not found, nothing to delete
    session.delete(schedule)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Schedule deleted successfully