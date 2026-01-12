from typing import Type
from sqlmodel import SQLModel

from app.utils.exceptions import EmptyPayloadError, NotFoundError

# Whitelist of valid table names to prevent SQL injection
VALID_TABLES = {
    "roles", "proficiency_levels", "event_types",
    "teams", "users", "team_users", "user_roles",
    "schedules", "events", "event_assignments", "user_unavailable_periods",
}

def require_non_empty_payload(payload: SQLModel) -> None:
    payload_dict = payload.model_dump(exclude_unset=True)
    if not payload_dict:
        raise EmptyPayloadError("Empty payload is not allowed.")
    return payload_dict

def raise_exception_if_not_found(obj: SQLModel | None, model: Type[SQLModel]) -> None:
    if not obj:
        raise NotFoundError(f"{model.__name__} not found")