from typing import TYPE_CHECKING, Type
from fastapi import HTTPException, status
from uuid import UUID
from sqlmodel import Session, SQLModel
from app.db.models import EventWithAssignmentsPublic, EventPublic, EventAssignmentEmbeddedPublic

if TYPE_CHECKING:
    from app.db.models import Schedule, Event

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

def get_or_raise_exception(session: Session, model: Type[SQLModel], id: UUID, http_status_code: int = status.HTTP_404_NOT_FOUND) -> SQLModel:
    """Get an object by ID, raising HTTPException if it is not found."""
    obj = session.get(model, id)
    raise_exception_if_not_found(obj, model, http_status_code)
    return obj

def raise_exception_if_not_found(obj: SQLModel | None, model: Type[SQLModel], http_status_code: int = status.HTTP_404_NOT_FOUND) -> None:
    """Raise HTTPException if an object is not found."""
    if not obj:
        raise HTTPException(status_code=http_status_code, detail=f"{model.__name__} not found")

def build_events_with_assignments_from_schedule(schedule: "Schedule") -> list["EventWithAssignmentsPublic"]:
    """Build a list of EventWithAssignmentsPublic from a Schedule."""
    events = []
    for event in schedule.events:
        events.append(
            EventWithAssignmentsPublic(
                event=EventPublic.from_objects(
                    event=event,
                    schedule=schedule,
                    event_type=event.event_type,
                    team=event.team,
                ),
                event_assignments=[
                    EventAssignmentEmbeddedPublic.from_objects(
                        event_assignment=ea,
                        role=ea.role,
                        assigned_user=ea.assigned_user,
                    ) for ea in event.event_assignments
                ],
            )
        )
    return events

def build_events_with_assignments_from_event(event: "Event") -> "EventWithAssignmentsPublic":
    """Build a EventWithAssignmentsPublic from an Event."""
    return EventWithAssignmentsPublic(
        event=EventPublic.from_objects(
            event=event,
            schedule=event.schedule,
            event_type=event.event_type,
            team=event.team,
        ),
        event_assignments=[
            EventAssignmentEmbeddedPublic.from_objects(
                event_assignment=ea,
                role=ea.role,
                assigned_user=ea.assigned_user,
            ) for ea in event.event_assignments
        ],
    )