from fastapi import APIRouter, Depends, status

from app.models.user_availability import UserAvailabilityCreate, UserAvailabilityUpdate, UserAvailabilityOut 
# from app.utils.supabase import SupabaseService
# from app.dependencies import get_supabase_service

router = APIRouter(prefix="/user_availability")

# @router.get("/", response_model=list[UserAvailabilityOut])
# async def get_user_availability(service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_all(table="user_availability")

# @router.get("/{id}", response_model=UserAvailabilityOut)
# async def get_user_availability(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_single(table="user_availability", id=id)

# @router.post("/", response_model=UserAvailabilityOut, status_code=status.HTTP_201_CREATED)
# async def post_user_availability(user_availability: UserAvailabilityCreate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = user_availability.model_dump(exclude_none=True)
#     payload["date"] = payload["date"].isoformat()
#     raw = service.post(table="user_availability", body=payload)
#     return UserAvailabilityOut(**raw)

# @router.patch("/{id}", response_model=UserAvailabilityOut)
# async def update_user_availability(id: str, user_availability: UserAvailabilityUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = user_availability.model_dump(exclude_none=True)

#     if "date" in payload:
#         payload["date"] = payload["date"].isoformat()
    
#     raw = service.update(table="user_availability", body=payload, id=id)
#     return UserAvailabilityOut(**raw)

# @router.delete("/{id}", response_model=UserAvailabilityOut)
# async def delete_user_availability(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="user_availability", id=id)
