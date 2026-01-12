from typing import TYPE_CHECKING
from app.db.models import EventWithAssignmentsPublic, EventPublic, EventAssignmentEmbeddedPublic

if TYPE_CHECKING:
    from app.db.models import Schedule, Event

def build_events_with_assignments_from_schedule(schedule: "Schedule") -> list["EventWithAssignmentsPublic"]:
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