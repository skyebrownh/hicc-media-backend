from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic
from app.utils.dependencies import SessionDep, ScheduleDep, ScheduleWithEventsAndAssignmentsDep
from app.services.domain import update_object, get_schedule_grid_from_schedule, create_object

router = APIRouter(prefix="/schedules")

@router.get("", response_model=list[Schedule])
def get_all_schedules(session: SessionDep):
    return session.exec(select(Schedule)).all()

@router.get("/{id}", response_model=Schedule)
def get_single_schedule(schedule: ScheduleDep):
    return schedule

@router.get("/{id}/grid", response_model=ScheduleGridPublic)
def get_schedule_grid(session: SessionDep, schedule: ScheduleWithEventsAndAssignmentsDep):
    return get_schedule_grid_from_schedule(session, schedule)

@router.post("", response_model=Schedule, status_code=status.HTTP_201_CREATED)
def post_schedule(payload: ScheduleCreate, session: SessionDep):
    return create_object(session, payload, Schedule, "schedule_check_month")
    
# TODO: Generate events for a schedule - using a service

@router.patch("/{id}", response_model=Schedule)
def patch_schedule(payload: ScheduleUpdate, session: SessionDep, schedule: ScheduleDep):
    return update_object(session, payload, schedule)

@router.delete("/{id}")
def delete_schedule(session: SessionDep, schedule: ScheduleDep):
    session.delete(schedule)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)