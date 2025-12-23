from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from sqlmodel import Session, select
from app.db.models import Team, TeamCreate, TeamUpdate
from app.utils.dependencies import get_db_session

router = APIRouter(prefix="/teams")

@router.get("", response_model=list[Team])
async def get_teams(session: Session = Depends(get_db_session)):
    return session.exec(select(Team)).all()

# @router.get("/{team_id}", response_model=TeamOut)
# async def get_team(team_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await fetch_one(conn, table="teams", filters={"team_id": team_id})

# @router.post("", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
# async def post_team(team: TeamCreate, conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await insert_team(conn, team=team)

# @router.patch("/{team_id}", response_model=TeamOut)
# async def patch_team(team_id: UUID, team_update: TeamUpdate | None = Body(default=None), conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await update_team(conn, team_id=team_id, payload=team_update)

# @router.delete("/{team_id}", response_model=TeamOut)
# async def delete_team(team_id: UUID, conn: asyncpg.Connection = Depends(get_db_connection)):
#         return await delete_one(conn, table="teams", filters={"team_id": team_id})