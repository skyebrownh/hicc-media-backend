from typing import Any, Type
from fastapi import HTTPException, status
from uuid import UUID
from sqlmodel import Session, SQLModel

# Whitelist of valid table names to prevent SQL injection
VALID_TABLES = {
    "roles",
    "proficiency_levels",
    "event_types",
    "teams",
    "users",
    "team_users",
    "user_roles",
    "schedules",
    "events",
    "event_assignments",
    "user_unavailable_periods",
}

def validate_table_name(table: str) -> None:
    """Validate that a table name is in the whitelist to prevent SQL injection."""
    if table not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}. Must be one of {sorted(VALID_TABLES)}")

def maybe(value: Any, attr: str):
    """Return the value of an attribute if it is not None, otherwise return None."""
    if value is None:
        return None
    return getattr(value, attr, None)

def raise_bad_request_empty_payload(payload):
    """Validate that a payload is not empty, raising HTTPException if it is."""
    if not payload:
        raise HTTPException(status_code=400, detail="Payload cannot be empty")

def get_or_404(session: Session, model: Type[SQLModel], id: UUID) -> Any:
    """Get an object by ID, raising HTTPException if it is not found."""
    obj = session.get(model, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return obj