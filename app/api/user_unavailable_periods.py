from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException, Response
from app.db.models import UserUnavailablePeriod, UserUnavailablePeriodCreate, UserUnavailablePeriodUpdate, UserUnavailablePeriodPublic
from sqlmodel import Session
from app.utils.dependencies import get_db_session

router = APIRouter()

# # Insert new user unavailable period
# @router.post("/user_unavailable_periods", response_model=UserDateOut, status_code=status.HTTP_201_CREATED)
# async def post_user_unavailable_period(user_unavailable_period: UserDateCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_user_unavailable_period(conn, user_unavailable_period=user_unavailable_period)

# # Insert user unavailable periods in bulk for a user
# @router.post("/user_unavailable_periods/bulk", response_model=list[UserDateOut], status_code=status.HTTP_201_CREATED)
# async def post_user_unavailable_periods_bulk(user_unavailable_periods: list[UserDateCreate], conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await insert_user_unavailable_periods(conn, user_unavailable_periods=user_unavailable_periods)

# # Update user unavailable period
# @router.patch("/users/{user_id}/dates/{date}", response_model=UserDateOut)
# async def patch_user_unavailable_period(
#     user_id: UUID,
#     date: datetime.date,
#     user_unavailable_period_update: UserDateUpdate | None = Body(default=None),
#     conn: asyncpg.Connection = Depends(get_db_connection),
# ):
#     return await update_user_unavailable_period(conn, user_id=user_id, date=date, payload=user_unavailable_period_update)

@router.delete("/user_availability/{id}")
async def delete_user_unavailable_period(id: UUID, session: Session = Depends(get_db_session)):
    """Delete a user unavailable period by ID"""
    user_unavailable_period = session.get(UserUnavailablePeriod, id)
    if not user_unavailable_period:
        return Response(status_code=status.HTTP_204_NO_CONTENT) # User unavailable period not found, nothing to delete
    session.delete(user_unavailable_period)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # User unavailable period deleted successfully