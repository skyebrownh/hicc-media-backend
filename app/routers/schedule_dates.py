from fastapi import APIRouter, Depends, status

from app.models.schedule_date import ScheduleDateCreate, ScheduleDateUpdate, ScheduleDateOut 
# from app.utils.supabase import SupabaseService
# from app.dependencies import get_supabase_service

router = APIRouter(prefix="/schedule_dates")

# @router.get("/", response_model=list[ScheduleDateOut])
# async def get_schedule_dates(service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_all(table="schedule_dates")

# @router.get("/{id}", response_model=ScheduleDateOut)
# async def get_schedule_date(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_single(table="schedule_dates", id=id)

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

# @router.delete("/{id}", response_model=ScheduleDateOut)
# async def delete_schedule_date(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="schedule_dates", id=id)
