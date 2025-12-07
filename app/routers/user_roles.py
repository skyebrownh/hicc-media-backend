from fastapi import APIRouter, Depends, status

from app.models.user_role import UserRoleCreate, UserRoleUpdate, UserRoleOut 
# from app.utils.supabase import SupabaseService
# from app.dependencies import get_supabase_service

router = APIRouter(prefix="/user_roles")

# @router.get("/", response_model=list[UserRoleOut])
# async def get_user_roles(service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_all(table="user_roles")

# @router.get("/{id}", response_model=UserRoleOut)
# async def get_user_role(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_single(table="user_roles", id=id)

# @router.post("/", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
# async def post_user_roles(user_role: UserRoleCreate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.post(table="user_roles", body=user_role.model_dump(exclude_none=True))

# @router.patch("/{id}", response_model=UserRoleOut)
# async def update_user_role(id: str, user_role: UserRoleUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="user_roles", body=user_role.model_dump(exclude_none=True), id=id)

# @router.delete("/{id}", response_model=UserRoleOut)
# async def delete_user_role(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="user_roles", id=id)

