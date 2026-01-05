from typing import TYPE_CHECKING, Type
from fastapi import HTTPException, status
from uuid import UUID
from sqlmodel import Session, SQLModel
from app.db.models import (
    EventWithAssignmentsPublic,
    EventPublic,
    EventAssignmentEmbeddedPublic,
)

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

def raise_bad_request_empty_payload(payload):
    """Validate that a payload is not empty, raising HTTPException if it is."""
    if not payload:
        raise HTTPException(status_code=400, detail="Payload cannot be empty")

def get_or_404(session: Session, model: Type[SQLModel], id: UUID) -> SQLModel:
    """Get an object by ID, raising HTTPException if it is not found."""
    obj = session.get(model, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return obj

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