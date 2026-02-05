from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import Team, TeamCreate, TeamUpdate
from app.utils.dependencies import SessionDep, TeamDep, default_depends, default_depends_with_admin
from app.services.domain import create_object, update_object, delete_object

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("", response_model=list[Team], dependencies=default_depends())
def get_all_teams(session: SessionDep):
    return session.exec(select(Team)).all()

@router.get("/{id}", response_model=Team, dependencies=default_depends())
def get_single_team(team: TeamDep):
    return team

@router.post("", response_model=Team, status_code=status.HTTP_201_CREATED, dependencies=default_depends_with_admin())
def post_team(payload: TeamCreate, session: SessionDep):
    return create_object(session, payload, Team)

@router.patch("/{id}", response_model=Team, dependencies=default_depends_with_admin())
def patch_team(payload: TeamUpdate, session: SessionDep, team: TeamDep):
    return update_object(session, payload, team)

@router.delete("/{id}", dependencies=default_depends_with_admin())
def delete_team(session: SessionDep, team: TeamDep):
    delete_object(session, team)
    return Response(status_code=status.HTTP_204_NO_CONTENT)