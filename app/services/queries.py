from uuid import UUID
from datetime import datetime, timezone
from calendar import monthrange
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.db.models import UserRole, User, Schedule, Event, EventAssignment, UserUnavailablePeriod

def select_schedule_with_events_and_assignments(session: Session, schedule_id: UUID) -> Schedule | None:
    return session.exec(
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(
            selectinload(Schedule.events).selectinload(Event.team),
            selectinload(Schedule.events).selectinload(Event.event_type),
            selectinload(Schedule.events).selectinload(Event.event_assignments).selectinload(EventAssignment.role),
            selectinload(Schedule.events).selectinload(Event.event_assignments).selectinload(EventAssignment.assigned_user)
        )
    ).one_or_none()

def select_event_with_full_hierarchy(session: Session, event_id: UUID) -> Event | None:
    return session.exec(
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.schedule),
            selectinload(Event.team),
            selectinload(Event.event_type),
            selectinload(Event.event_assignments).selectinload(EventAssignment.role),
            selectinload(Event.event_assignments).selectinload(EventAssignment.assigned_user).selectinload(User.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).one_or_none()

def select_full_event_assignment(session: Session, event_assignment_id: UUID) -> EventAssignment | None:
    return session.exec(
        select(EventAssignment)
        .where(EventAssignment.id == event_assignment_id)
        .options(
            selectinload(EventAssignment.event),
            selectinload(EventAssignment.role),
            selectinload(EventAssignment.assigned_user).selectinload(User.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).one_or_none()

def select_unavailable_users_for_month(session: Session, month: int, year: int) -> list[UserUnavailablePeriod]:
    # Calculate the start and end of the month in UTC
    month_start = datetime(year, month, 1, tzinfo=timezone.utc)
    _, last_day = monthrange(year, month)
    month_end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    
    # Find all periods that overlap with the month
    # A period overlaps if: starts_at < month_end AND ends_at > month_start
    return session.exec(
        select(UserUnavailablePeriod)
        .where(UserUnavailablePeriod.starts_at < month_end)
        .where(UserUnavailablePeriod.ends_at > month_start)
        .options(selectinload(UserUnavailablePeriod.user))
    ).all()