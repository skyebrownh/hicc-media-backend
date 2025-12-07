from fastapi import APIRouter, Depends, status

from app.models.proficiency_level import ProficiencyLevelCreate, ProficiencyLevelUpdate, ProficiencyLevelOut 
# from app.utils.supabase import SupabaseService
# from app.dependencies import get_supabase_service

router = APIRouter(prefix="/proficiency_levels")

# @router.get("/", response_model=list[ProficiencyLevelOut])
# async def get_proficiency_levels(service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_all(table="proficiency_levels")

# @router.get("/{id}", response_model=ProficiencyLevelOut)
# async def get_proficiency_level(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.get_single(table="proficiency_levels", id=id)

# @router.post("/", response_model=ProficiencyLevelOut, status_code=status.HTTP_201_CREATED)
# async def post_proficiency_levels(proficiency_level: ProficiencyLevelCreate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.post(table="proficiency_levels", body=proficiency_level.model_dump(exclude_none=True))

# @router.patch("/{id}", response_model=ProficiencyLevelOut)
# async def update_proficiency_level(id: str, proficiency_level: ProficiencyLevelUpdate, service: SupabaseService = Depends(get_supabase_service)):
#     return service.update(table="proficiency_levels", body=proficiency_level.model_dump(exclude_none=True), id=id)

# @router.delete("/{id}", response_model=ProficiencyLevelOut)
# async def delete_proficiency_level(id: str, service: SupabaseService = Depends(get_supabase_service)):
#     return service.delete(table="proficiency_levels", id=id)