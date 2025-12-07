from fastapi import APIRouter, Depends, status

from app.models.date import DateCreate, DateUpdate, DateOut 
# from app.utils.supabase import SupabaseService
# from app.dependencies import get_supabase_service

router = APIRouter(prefix="/dates")

# @router.get("/", response_model=list[DateOut])
# async def get_dates(service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_all(table="dates")

# @router.get("/{id}", response_model=DateOut)
# async def get_date(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_single(table="dates", id=id)

# @router.post("/", response_model=DateOut, status_code=status.HTTP_201_CREATED)
# async def post_dates(date: DateCreate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = date.model_dump(exclude_none=True)
#     payload["date"] = payload["date"].isoformat()
#     raw = service.post(table="dates", body=payload)
#     return DateOut(**raw)

# @router.patch("/{id}", response_model=DateOut)
# async def update_date(id: str, date: DateUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="dates", body=date.model_dump(exclude_none=True), id=id)

# @router.delete("/{id}", response_model=DateOut)
# async def delete_date(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="dates", id=id)