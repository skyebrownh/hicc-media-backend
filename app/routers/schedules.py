from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from app.db.models import Schedule, ScheduleCreate, ScheduleUpdate
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session

router = APIRouter(prefix="/schedules")

# Get all schedules
@router.get("", response_model=list[Schedule])
async def get_schedules(session: Session = Depends(get_db_session)):
    return session.exec(select(Schedule)).all()
    
# # Get all schedule_dates for a schedule
# @router.get("/{schedule_id}/schedule_dates", response_model=list[ScheduleDateOut])
# async def get_schedule_dates_for_schedule(schedule_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     # Verify schedule exists first (will raise 404 if not found)
#     await fetch_one(conn, table="schedules", filters={"schedule_id": schedule_id})
#     return await fetch_all(conn, table="schedule_dates", filters={"schedule_id": schedule_id})

# # Get single schedule
# @router.get("/{schedule_id}", response_model=ScheduleOut)
# async def get_schedule(schedule_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await fetch_one(conn, table="schedules", filters={"schedule_id": schedule_id})

# # Insert new schedule
# @router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
# async def post_schedule(schedule: ScheduleCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_schedule(conn, schedule=schedule)
    
# # TODO: Insert schedule dates for a schedule based on configuration

# # Update schedule
# @router.patch("/{schedule_id}", response_model=ScheduleOut)
# async def patch_schedule(
#     schedule_id: UUID,
#     schedule_update: ScheduleUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_schedule(conn, schedule_id=schedule_id, payload=schedule_update)

# # Delete schedule
# @router.delete("/{schedule_id}", response_model=ScheduleOut)
# async def delete_schedule(schedule_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="schedules", filters={"schedule_id": schedule_id})
    
# # Delete schedule dates for a schedule
# @router.delete("/{schedule_id}/schedule_dates", response_model=list[ScheduleDateOut])
# async def delete_schedule_dates_for_schedule(schedule_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#     # Verify schedule exists first (will raise 404 if not found)
#     await fetch_one(conn, table="schedules", filters={"schedule_id": schedule_id})
#     return await delete_all(conn, table="schedule_dates", filters={"schedule_id": schedule_id})