from fastapi import APIRouter, Depends, status
from app.models import ScheduleCreate, ScheduleUpdate, ScheduleOut 
from app.db.queries import fetch_all, fetch_one, delete_one
from app.db.database import get_db_pool

router = APIRouter(prefix="/schedules")

@router.get("/", response_model=list[ScheduleOut])
async def get_schedules(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedules")

@router.get("/{id}", response_model=ScheduleOut)
async def get_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedules", id=id)

# @router.post("/", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
# async def post_schedules(schedule: ScheduleCreate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = schedule.model_dump(exclude_none=True)
#     payload["month_start_date"] = payload["month_start_date"].isoformat()
#     raw = service.post(table="schedules", body=payload)
#     return ScheduleOut(**raw)

# @router.patch("/{id}", response_model=ScheduleOut)
# async def update_schedule(id: str, schedule: ScheduleUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = schedule.model_dump(exclude_none=True)

#     if "month_start_date" in payload:
#         payload["month_start_date"] = payload["month_start_date"].isoformat()

#     raw = service.update(table="schedules", body=payload, id=id)
#     return ScheduleOut(**raw) 

@router.delete("/{id}", response_model=ScheduleOut)
async def delete_schedule(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="schedules", id=id)