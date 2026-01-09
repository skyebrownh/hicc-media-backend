from uuid import UUID
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.db.models import UserRole, User, Role, Schedule, Event, EventAssignment, UserUnavailablePeriod, Team, TeamUser

def get_role(session: Session, role_id: UUID) -> Role | None:
    return session.exec(
        select(Role)
        .where(Role.id == role_id)
        .options(
            selectinload(Role.user_roles)
        )
    ).one_or_none()

def get_team(session: Session, team_id: UUID) -> Team | None:
    return session.exec(
        select(Team)
        .where(Team.id == team_id)
        .options(
            selectinload(Team.team_users)
            .selectinload(TeamUser.user))
        ).one_or_none()

def get_user(session: Session, user_id: UUID) -> User | None:
    return session.exec(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.user_roles)
        )
    ).one_or_none()

def get_team_user(session: Session, team_id: UUID, user_id: UUID) -> TeamUser | None:
    return session.exec(
        select(TeamUser)
        .where(TeamUser.team_id == team_id)
        .where(TeamUser.user_id == user_id)
    ).one_or_none()

def get_user_for_user_roles(session: Session, user_id: UUID) -> User | None:
    return session.exec(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.user_roles).selectinload(UserRole.role),
            selectinload(User.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).one_or_none()

def get_role_for_user_roles(session: Session, role_id: UUID) -> Role | None:
    return session.exec(
        select(Role)
        .where(Role.id == role_id)
        .options(
            selectinload(Role.user_roles).selectinload(UserRole.user),
            selectinload(Role.user_roles).selectinload(UserRole.proficiency_level)
        )
    ).one_or_none()

def get_schedule(session: Session, schedule_id: UUID) -> Schedule | None:
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

def get_schedule_for_cascade_delete(session: Session, schedule_id: UUID) -> Schedule | None:
    return session.exec(
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(
            selectinload(Schedule.events)
        )
    ).one_or_none()

def get_schedule_only(session: Session, schedule_id: UUID) -> Schedule | None:
    return session.exec(
        select(Schedule)
        .where(Schedule.id == schedule_id)
    ).one_or_none()

def get_event(session: Session, event_id: UUID) -> Event | None:
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

def get_event_for_cascade_delete(session: Session, event_id: UUID) -> Event | None:
    return session.exec(
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.event_assignments)
        )
    ).one_or_none()

def get_unavailable_users_for_event(session: Session, event_id: UUID) -> list[User]:
    event = session.exec(
        select(Event)
        .where(Event.id == event_id)
    ).one_or_none()

    if not event:
        return []

    return session.exec(
        select(UserUnavailablePeriod)
        .where(UserUnavailablePeriod.starts_at < event.ends_at)
        .where(UserUnavailablePeriod.ends_at > event.starts_at)
        .options(selectinload(UserUnavailablePeriod.user))
    ).all()