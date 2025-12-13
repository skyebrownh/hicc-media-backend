import datetime
from fastapi import APIRouter, Depends, Body, status
from app.models import DateCreate, DateUpdate, DateOut 
from app.db.queries import fetch_all, fetch_one, delete_one, insert_date, update_date
from app.db.database import get_db_pool

router = APIRouter(prefix="/dates")

@router.get("", response_model=list[DateOut])
async def get_dates(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_all(conn, table="dates")

@router.get("/{date}", response_model=DateOut)
async def get_date(date: datetime.date, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await fetch_one(conn, table="dates", filters={"date": date})
    
# TODO: Insert all dates for a given year

@router.post("", response_model=DateOut, status_code=status.HTTP_201_CREATED)
async def post_date(date: DateCreate, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await insert_date(conn, date_obj=date)

@router.patch("/{date}", response_model=DateOut)
async def patch_date(
    date: datetime.date,
    date_update: DateUpdate | None = Body(default=None),
    pool=Depends(get_db_pool),
):
    async with pool.acquire() as conn:
        return await update_date(conn, date=date, payload=date_update)

@router.delete("/{date}", response_model=DateOut)
async def delete_date(date: datetime.date, pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        return await delete_one(conn, table="dates", filters={"date": date})