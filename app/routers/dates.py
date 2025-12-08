from fastapi import APIRouter, Depends, status
from app.models import DateCreate, DateUpdate, DateOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_date
from app.db.database import get_db_pool

router = APIRouter(prefix="/dates")

@router.get("/", response_model=list[DateOut])
async def get_dates(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="dates")

@router.get("/{id}", response_model=DateOut)
async def get_date(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="dates", id=id)

@router.post("/", response_model=DateOut, status_code=status.HTTP_201_CREATED)
async def post_date(date: DateCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_date(conn, date_obj=date)

# @router.patch("/{id}", response_model=DateOut)
# async def update_date(id: str, date: DateUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="dates", body=date.model_dump(exclude_none=True), id=id)

@router.delete("/{id}", response_model=DateOut)
async def delete_date(id: str, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="dates", id=id)