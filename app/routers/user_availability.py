from fastapi import APIRouter, Depends, status
from app.models import UserAvailabilityCreate, UserAvailabilityUpdate, UserAvailabilityOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_user_availability
from app.db.database import get_db_pool

router = APIRouter(prefix="/user_availability")

@router.get("/", response_model=list[UserAvailabilityOut])
async def get_user_availability(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="user_availability")

@router.get("/{id}", response_model=UserAvailabilityOut)
async def get_user_availability(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="user_availability", id=id)

@router.post("/", response_model=UserAvailabilityOut, status_code=status.HTTP_201_CREATED)
async def post_user_availability(user_availability: UserAvailabilityCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_user_availability(conn, user_availability=user_availability)

# @router.patch("/{id}", response_model=UserAvailabilityOut)
# async def update_user_availability(id: str, user_availability: UserAvailabilityUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     payload = user_availability.model_dump(exclude_none=True)

#     if "date" in payload:
#         payload["date"] = payload["date"].isoformat()
    
#     raw = service.update(table="user_availability", body=payload, id=id)
#     return UserAvailabilityOut(**raw)

@router.delete("/{id}", response_model=UserAvailabilityOut)
async def delete_user_availability(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="user_availability", id=id)