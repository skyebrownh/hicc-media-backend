from fastapi import APIRouter, status, Response

from app.db.models import UserUnavailablePeriodCreate, UserUnavailablePeriodUpdate, UserUnavailablePeriodPublic
from app.utils.dependencies import SessionDep, UserWithUserRolesForUnavailablePeriodsDep, UserUnavailablePeriodDep
from app.services.domain import create_user_unavailable_period, create_user_unavailable_periods_bulk, update_user_unavailable_period

router = APIRouter()

@router.post("/users/{user_id}/availability", response_model=UserUnavailablePeriodPublic, status_code=status.HTTP_201_CREATED)
def post_user_unavailable_period(user: UserWithUserRolesForUnavailablePeriodsDep, payload: UserUnavailablePeriodCreate, session: SessionDep):
    return create_user_unavailable_period(session, payload, user)

@router.post("/users/{user_id}/availability/bulk", response_model=list[UserUnavailablePeriodPublic], status_code=status.HTTP_201_CREATED)
def post_user_unavailable_periods_bulk(user: UserWithUserRolesForUnavailablePeriodsDep, payload: list[UserUnavailablePeriodCreate], session: SessionDep):
    return create_user_unavailable_periods_bulk(session, payload, user)

@router.patch("/user_availability/{id}", response_model=UserUnavailablePeriodPublic)
def patch_user_unavailable_period(payload: UserUnavailablePeriodUpdate, session: SessionDep, user_unavailable_period: UserUnavailablePeriodDep):
    return update_user_unavailable_period(session, payload, user_unavailable_period)

@router.delete("/user_availability/{id}")
def delete_user_unavailable_period(session: SessionDep, user_unavailable_period: UserUnavailablePeriodDep):
    session.delete(user_unavailable_period)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)