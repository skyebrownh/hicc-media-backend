from fastapi import APIRouter, status, Response, Depends
from sqlmodel import select

from app.db.models import User, UserCreate, UserUpdate
from app.utils.dependencies import SessionDep, UserDep, require_admin, verify_api_key, get_optional_bearer_token, get_db_session
from app.services.domain import create_user_with_user_roles, update_object, delete_object

router = APIRouter(
    prefix="/users", 
    tags=["users"], 
    dependencies=[Depends(verify_api_key), Depends(get_optional_bearer_token), Depends(get_db_session)]
)

@router.get("", response_model=list[User])
def get_all_users(session: SessionDep):
    return session.exec(select(User)).all()

@router.get("/{id}", response_model=User)
def get_single_user(user: UserDep):
    return user

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_user(payload: UserCreate, session: SessionDep):
    return create_user_with_user_roles(session, payload)

@router.patch("/{id}", response_model=User, dependencies=[Depends(require_admin)])
def patch_user(payload: UserUpdate, session: SessionDep, user: UserDep):
    return update_object(session, payload, user)

@router.delete("/{id}", dependencies=[Depends(require_admin)])
def delete_user(session: SessionDep, user: UserDep):
    delete_object(session, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)