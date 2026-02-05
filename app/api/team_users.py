from fastapi import APIRouter, status, Response, Depends

from app.db.models import TeamUser, TeamUserCreate, TeamUserUpdate, TeamUserPublic
from app.utils.dependencies import SessionDep, TeamWithTeamUsersDep, TeamForTeamUsersDep, TeamUserDep, require_admin, verify_api_key, get_optional_bearer_token, get_db_session
from app.services.domain import create_team_user_for_team, update_team_user, delete_object

router = APIRouter(
    tags=["team_users"], 
    dependencies=[Depends(verify_api_key), Depends(get_optional_bearer_token), Depends(get_db_session)]
)

@router.get("/teams/{team_id}/users", response_model=list[TeamUserPublic])
def get_team_users_for_team(team: TeamWithTeamUsersDep):
    return [
        TeamUserPublic.from_objects(team_user=tu, team=team, user=tu.user)
        for tu in team.team_users
    ]

@router.post("/teams/{team_id}/users", response_model=TeamUser, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_team_user_for_team(payload: TeamUserCreate, session: SessionDep, team: TeamForTeamUsersDep):
    return create_team_user_for_team(session, payload, team)

@router.patch("/teams/{team_id}/users/{user_id}", response_model=TeamUserPublic, dependencies=[Depends(require_admin)])
def patch_team_user(payload: TeamUserUpdate, session: SessionDep, team_user: TeamUserDep):
    return update_team_user(session, payload, team_user)

@router.delete("/teams/{team_id}/users/{user_id}", dependencies=[Depends(require_admin)])
def delete_team_user(session: SessionDep, team_user: TeamUserDep):
    delete_object(session, team_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)