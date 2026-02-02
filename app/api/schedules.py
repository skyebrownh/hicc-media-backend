from fastapi import APIRouter, status, Response, Depends
from sqlmodel import select

from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic
from app.utils.dependencies import SessionDep, ScheduleDep, ScheduleWithEventsAndAssignmentsDep, require_admin
from app.services.domain import update_object, get_schedule_grid_from_schedule, create_object, delete_object

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("", response_model=list[Schedule])
def get_all_schedules(session: SessionDep):
    return session.exec(select(Schedule)).all()

@router.get("/{id}", response_model=Schedule)
def get_single_schedule(schedule: ScheduleDep):
    return schedule

@router.get("/{id}/grid", response_model=ScheduleGridPublic)
def get_schedule_grid(session: SessionDep, schedule: ScheduleWithEventsAndAssignmentsDep):
    return get_schedule_grid_from_schedule(session, schedule)

@router.post("", response_model=Schedule, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_schedule(payload: ScheduleCreate, session: SessionDep):
    return create_object(session, payload, Schedule, "schedule_check_month")

@router.patch("/{id}", response_model=Schedule, dependencies=[Depends(require_admin)])
def patch_schedule(payload: ScheduleUpdate, session: SessionDep, schedule: ScheduleDep):
    return update_object(session, payload, schedule)

@router.delete("/{id}", dependencies=[Depends(require_admin)])
def delete_schedule(session: SessionDep, schedule: ScheduleDep):
    delete_object(session, schedule)
    return Response(status_code=status.HTTP_204_NO_CONTENT)