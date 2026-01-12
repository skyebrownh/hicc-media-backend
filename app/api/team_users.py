from fastapi import APIRouter, status, Response

from app.db.models import TeamUser, TeamUserCreate, TeamUserUpdate, TeamUserPublic
from app.utils.dependencies import SessionDep, TeamWithTeamUsersDep, TeamForTeamUsersDep, TeamUserDep
from app.services.domain import create_team_user_for_team, update_team_user

router = APIRouter()

@router.get("/teams/{team_id}/users", response_model=list[TeamUserPublic])
def get_team_users_for_team(team: TeamWithTeamUsersDep):
    return [
        TeamUserPublic.from_objects(team_user=tu, team=team, user=tu.user)
        for tu in team.team_users
    ]

@router.post("/teams/{team_id}/users", response_model=TeamUser, status_code=status.HTTP_201_CREATED)
def post_team_user_for_team(payload: TeamUserCreate, session: SessionDep, team: TeamForTeamUsersDep):
    return create_team_user_for_team(session, payload, team)

@router.patch("/teams/{team_id}/users/{user_id}", response_model=TeamUserPublic)
def patch_team_user(payload: TeamUserUpdate, session: SessionDep, team_user: TeamUserDep):
    return update_team_user(session, payload, team_user)

@router.delete("/teams/{team_id}/users/{user_id}")
def delete_team_user(session: SessionDep, team_user: TeamUserDep):
    session.delete(team_user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)