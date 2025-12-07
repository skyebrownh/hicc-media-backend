from fastapi import APIRouter, Depends, status
from app.models import ScheduleDateCreate, ScheduleDateUpdate, ScheduleDateOut 
from app.db.queries import fetch_all, fetch_one, delete_one
from app.db.database import get_db_pool

router = APIRouter(prefix="/schedule_dates")

@router.get("/", response_model=list[ScheduleDateOut])
async def get_schedule_dates(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedule_dates")

@router.get("/{id}", response_model=ScheduleDateOut)
async def get_schedule_date(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedule_dates", id=id)

# @router.post("/", response_model=ScheduleDateOut, status_code=status.HTTP_201_CREATED)
# async def post_schedule_dates(schedule_date: ScheduleDateCreate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = schedule_date.model_dump(exclude_none=True)
#     payload["date"] = payload["date"].isoformat()
#     raw = service.post(table="schedule_dates", body=payload)
#     return ScheduleDateOut(**raw)

# @router.patch("/{id}", response_model=ScheduleDateOut)
# async def update_schedule_date(id: str, schedule_date: ScheduleDateUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = schedule_date.model_dump(exclude_none=True)

#     if "date" in payload:
#         payload["date"] = payload["date"].isoformat()

#     raw = service.update(table="schedule_dates", body=payload, id=id)
#     return ScheduleDateOut(**raw) 

@router.delete("/{id}", response_model=ScheduleDateOut)
async def delete_schedule_date(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="schedule_dates", id=id)