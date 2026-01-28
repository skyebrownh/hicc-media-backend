from typing import Type
from sqlmodel import SQLModel

from app.utils.exceptions import EmptyPayloadError, NotFoundError

# OpenAPI tags metadata for the API
TAGS_METADATA = [
    {
        "name": "health",
        "description": "Health check endpoint that verifies application and database connectivity",
    },
    {
        "name": "roles",
        "description": "Role are the skills/positions that can be assigned to users and identify slots for event assignments",
    },
    {
        "name": "proficiency_levels",
        "description": "Proficiency levels are the levels of expertise for a role",
    },
    {
        "name": "event_types",
        "description": "Event types are the types of events that can be created",
    },
    {
        "name": "teams",
        "description": "Teams are groups of users that work together on events",
    },
    {
        "name": "users",
        "description": "Users are the people who work on events",
    },
    {
        "name": "team_users",
        "description": "Team users are the users who are part of a team",
    },
    {
        "name": "user_roles",
        "description": "User roles are the roles that a user has",
    },
    {
        "name": "schedules",
        "description": "Schedules are the time periods that events can be assigned to (month-long)",
    },
    {
        "name": "events",
        "description": "Events are the individual occurrences within a schedule",
    },
    {
        "name": "event_assignments",
        "description": "Event assignments are the assignments of a user to a role for an event",
    },
    {
        "name": "user_unavailable_periods",
        "description": "User unavailable periods are the time periods that a user is unavailable",
    },
]

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