from fastapi import APIRouter, status, Response, Depends

from app.db.models import UserUnavailablePeriodCreate, UserUnavailablePeriodUpdate, UserUnavailablePeriodPublic
from app.utils.dependencies import SessionDep, UserWithUserRolesForUnavailablePeriodsDep, UserUnavailablePeriodDep, require_admin, verify_api_key, get_optional_bearer_token, get_db_session
from app.services.domain import create_user_unavailable_period, create_user_unavailable_periods_bulk, update_user_unavailable_period, delete_object

router = APIRouter(
    tags=["user_unavailable_periods"], 
    dependencies=[Depends(verify_api_key), Depends(get_optional_bearer_token), Depends(get_db_session)]
)

@router.post("/users/{user_id}/availability", 
    response_model=UserUnavailablePeriodPublic, 
    status_code=status.HTTP_201_CREATED, 
    dependencies=[Depends(require_admin)]
)
def post_user_unavailable_period(
    user: UserWithUserRolesForUnavailablePeriodsDep, 
    payload: UserUnavailablePeriodCreate, 
    session: SessionDep
):
    return create_user_unavailable_period(session, payload, user)

@router.post("/users/{user_id}/availability/bulk", 
    response_model=list[UserUnavailablePeriodPublic], 
    status_code=status.HTTP_201_CREATED, 
    dependencies=[Depends(require_admin)]
)
def post_user_unavailable_periods_bulk(
    user: UserWithUserRolesForUnavailablePeriodsDep, 
    payload: list[UserUnavailablePeriodCreate], 
    session: SessionDep,
):
    return create_user_unavailable_periods_bulk(session, payload, user)

@router.patch("/user_availability/{id}", 
    response_model=UserUnavailablePeriodPublic, 
    dependencies=[Depends(require_admin)]
)
def patch_user_unavailable_period(
    payload: UserUnavailablePeriodUpdate, 
    session: SessionDep, 
    user_unavailable_period: UserUnavailablePeriodDep
):
    return update_user_unavailable_period(session, payload, user_unavailable_period)

@router.delete("/user_availability/{id}", dependencies=[Depends(require_admin)])
def delete_user_unavailable_period(session: SessionDep, user_unavailable_period: UserUnavailablePeriodDep):
    delete_object(session, user_unavailable_period)
    return Response(status_code=status.HTTP_204_NO_CONTENT)