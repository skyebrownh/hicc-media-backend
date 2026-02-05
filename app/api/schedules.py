from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic
from app.utils.dependencies import SessionDep, ScheduleDep, ScheduleWithEventsAndAssignmentsDep, default_depends, default_depends_with_admin
from app.services.domain import update_object, get_schedule_grid_from_schedule, create_object, delete_object

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("", response_model=list[Schedule], dependencies=default_depends())
def get_all_schedules(session: SessionDep):
    return session.exec(select(Schedule)).all()

@router.get("/{id}", response_model=Schedule, dependencies=default_depends())
def get_single_schedule(schedule: ScheduleDep):
    return schedule

@router.get("/{id}/grid", response_model=ScheduleGridPublic, dependencies=default_depends())
def get_schedule_grid(session: SessionDep, schedule: ScheduleWithEventsAndAssignmentsDep):
    return get_schedule_grid_from_schedule(session, schedule)

@router.post("", response_model=Schedule, status_code=status.HTTP_201_CREATED, dependencies=default_depends_with_admin())
def post_schedule(payload: ScheduleCreate, session: SessionDep):
    return create_object(session, payload, Schedule, "schedule_check_month")

@router.patch("/{id}", response_model=Schedule, dependencies=default_depends_with_admin())
def patch_schedule(payload: ScheduleUpdate, session: SessionDep, schedule: ScheduleDep):
    return update_object(session, payload, schedule)

@router.delete("/{id}", dependencies=default_depends_with_admin())
def delete_schedule(session: SessionDep, schedule: ScheduleDep):
    delete_object(session, schedule)
    return Response(status_code=status.HTTP_204_NO_CONTENT)