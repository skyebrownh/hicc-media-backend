from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic, EventWithAssignmentsPublic, Event, EventAssignment
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from app.utils.helpers import get_or_404
from app.services.scheduling import get_schedule

router = APIRouter(prefix="/schedules")

@router.get("", response_model=list[Schedule])
async def get_all_schedules(session: Session = Depends(get_db_session)):
    """Get all schedules"""
    return session.exec(select(Schedule)).all()

@router.get("/{id}", response_model=Schedule)
async def get_single_schedule(id: UUID, session: Session = Depends(get_db_session)):
    """Get a schedule by ID"""
    return get_or_404(session, Schedule, id)

# @router.get("/{id}/grid", response_model=list[ScheduleGridPublic])
# async def get_schedule_grid(id: UUID, session: Session = Depends(get_db_session)):
#     """Get a schedule grid by ID"""
#     schedule = get_schedule(session, id)
#     if not schedule:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

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