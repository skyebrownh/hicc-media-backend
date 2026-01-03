from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, HTTPException
from app.db.models import UserUnavailablePeriod, UserUnavailablePeriodCreate, UserUnavailablePeriodUpdate, UserUnavailablePeriodPublic, Event
from sqlmodel import Session, select
from app.utils.dependencies import get_db_session
from sqlalchemy.orm import selectinload

router = APIRouter()

# @router.get("/events/{event_id}/unavailable-users", response_model=list[UserUnavailablePeriodPublic])
# async def get_unavailable_users_for_event(event_id: UUID, session: Session = Depends(get_db_session)):
#     """Get all unavailable users for an event"""
#     event = session.exec(
#         select(Event)
#         .where(Event.id == event_id)
#     ).one_or_none()
#     if not event:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

#     unavailable_users = session.exec(
#         select(UserUnavailablePeriod)
#         .where(UserUnavailablePeriod.starts_at < event.ends_at)
#         .where(UserUnavailablePeriod.ends_at > event.starts_at)
#         .options(selectinload(UserUnavailablePeriod.user))
#     ).all()
#     return [
#         UserUnavailablePeriodPublic(
#             id=upa.id,
#             user_id=upa.user_id,
#             starts_at=upa.starts_at,
#             ends_at=upa.ends_at,
#             user_first_name=upa.user.first_name,
#             user_last_name=upa.user.last_name,
#             user_email=upa.user.email,
#             user_phone=upa.user.phone,
#             user_is_active=upa.user.is_active,
#         )
#         for upa in unavailable_users
#     ]

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

# # Delete user unavailable period
# @router.delete("/users/{user_id}/dates/{date}", response_model=UserDateOut)
# async def delete_user_unavailable_period(user_id: UUID, date: datetime.date, conn: asyncpg.Connection = Depends(get_db_connection)):
#     return await delete_one(conn, table="user_unavailable_periods", filters={"user_id": user_id, "date": date})
