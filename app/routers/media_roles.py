from fastapi import APIRouter, Depends, status

from app.models.media_role import MediaRoleCreate, MediaRoleUpdate, MediaRoleOut 
# from app.utils.supabase import SupabaseService
# from app.dependencies import get_supabase_service

router = APIRouter(prefix="/media_roles")

# @router.get("/", response_model=list[MediaRoleOut])
# async def get_media_roles(service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_all(table="media_roles")

# @router.get("/{id}", response_model=MediaRoleOut)
# async def get_media_role(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_single(table="media_roles", id=id)

# @router.post("/", response_model=MediaRoleOut, status_code=status.HTTP_201_CREATED)
# async def post_media_roles(media_role: MediaRoleCreate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.post(table="media_roles", body=media_role.model_dump(exclude_none=True))

# @router.patch("/{id}", response_model=MediaRoleOut)
# async def update_media_role(id: str, media_role: MediaRoleUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="media_roles", body=media_role.model_dump(exclude_none=True), id=id)

# @router.delete("/{id}", response_model=MediaRoleOut)
# async def delete_media_role(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="media_roles", id=id)