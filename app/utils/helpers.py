from typing import Type
from fastapi import HTTPException, status
from sqlmodel import SQLModel

# Whitelist of valid table names to prevent SQL injection
VALID_TABLES = {
    "roles", "proficiency_levels", "event_types",
    "teams", "users", "team_users", "user_roles",
    "schedules", "events", "event_assignments", "user_unavailable_periods",
}

def require_non_empty_payload(payload: SQLModel) -> None:
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty payload is not allowed.")
    return payload_dict

def raise_exception_if_not_found(obj: SQLModel | None, model: Type[SQLModel], http_status_code: int = status.HTTP_404_NOT_FOUND) -> None:
    """Raise HTTPException if an object is not found."""
    if not obj:
        raise HTTPException(status_code=http_status_code, detail=f"{model.__name__} not found")