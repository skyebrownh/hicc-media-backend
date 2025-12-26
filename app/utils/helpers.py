import datetime
from typing import Any
from asyncpg import Connection, Record, exceptions
from fastapi import HTTPException

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