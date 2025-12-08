from fastapi import APIRouter, Depends, status
from app.models import ScheduleDateTypeCreate, ScheduleDateTypeUpdate, ScheduleDateTypeOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_schedule_date_type
from app.db.database import get_db_pool

router = APIRouter(prefix="/schedule_date_types")

@router.get("/", response_model=list[ScheduleDateTypeOut])
async def get_schedule_date_types(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="schedule_date_types")

@router.get("/{id}", response_model=ScheduleDateTypeOut)
async def get_schedule_date_type(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="schedule_date_types", id=id)

@router.post("/", response_model=ScheduleDateTypeOut, status_code=status.HTTP_201_CREATED)
async def post_schedule_date_type(schedule_date_type: ScheduleDateTypeCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_schedule_date_type(conn, schedule_date_type=schedule_date_type)

# @router.patch("/{id}", response_model=ScheduleDateTypeOut)
# async def update_schedule_date_type(id: str, schedule_date_type: ScheduleDateTypeUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="schedule_date_types", body=schedule_date_type.model_dump(exclude_none=True), id=id)

@router.delete("/{id}", response_model=ScheduleDateTypeOut)
async def delete_schedule_date_type(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="schedule_date_types", id=id)