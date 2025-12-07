from fastapi import APIRouter, Depends, status

from app.models.team_user import TeamUserCreate, TeamUserUpdate, TeamUserOut 
# from app.utils.supabase import SupabaseService
# from app.dependencies import get_supabase_service

router = APIRouter(prefix="/team_users")

# @router.get("/", response_model=list[TeamUserOut])
# async def get_team_users(service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_all(table="team_users")

# @router.get("/{id}", response_model=TeamUserOut)
# async def get_team_user(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_single(table="team_users", id=id)

# @router.post("/", response_model=TeamUserOut, status_code=status.HTTP_201_CREATED)
# async def post_team_users(team_user: TeamUserCreate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.post(table="team_users", body=team_user.model_dump(exclude_none=True))

# @router.patch("/{id}", response_model=TeamUserOut)
# async def update_team_user(id: str, team_user: TeamUserUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="team_users", body=team_user.model_dump(exclude_none=True), id=id)

# @router.delete("/{id}", response_model=TeamUserOut)
# async def delete_team_user(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="team_users", id=id)
