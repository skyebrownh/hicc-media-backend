from typing import Type
from sqlmodel import Session, select, SQLModel
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    Role, Team, User, UserRole, UserRoleUpdate, UserRolePublic, ProficiencyLevel, RoleCreate, UserCreate, 
    Schedule, EventPublic, ScheduleGridPublic, TeamUser, TeamUserCreate, TeamUserUpdate, TeamUserPublic,
    Event, EventCreate, EventAssignment, EventAssignmentPublic, EventAssignmentUpdate,
    EventWithAssignmentsAndAvailabilityPublic, 
    EventAssignmentEmbeddedPublic, 
    UserUnavailablePeriodEmbeddedPublic)
from app.utils.helpers import require_non_empty_payload
from app.utils.exceptions import ConflictError, CheckConstraintError
from app.services.queries import select_unavailable_users_for_event

# =============================
# CREATE OBJECT
# =============================
def create_object(session: Session, payload: SQLModel, model: Type[SQLModel], check_constraint: str | None = None) -> SQLModel:
    try:
        object = model.model_validate(payload)
        session.add(object)
        session.commit()
        session.refresh(object)
        return object
    except IntegrityError as e:
        session.rollback()
        if check_constraint and check_constraint in str(e):
            raise CheckConstraintError(f"{model.__name__} creation violates check constraint") from e
        raise ConflictError(f"{model.__name__} creation violates a constraint") from e

# =============================
# UPDATE OBJECT
# =============================
def update_object(session: Session, payload: SQLModel, object: SQLModel) -> SQLModel:
    try:
        payload_dict = require_non_empty_payload(payload)
        for key, value in payload_dict.items():
            setattr(object, key, value)
        session.commit()
        session.refresh(object)
        return object
    except IntegrityError as e:
        session.rollback()
        raise ConflictError(f"{object.__class__.__name__} update violates a constraint") from e

# =============================
# CREATE ROLE WITH USER ROLES
# =============================
def create_role_with_user_roles(session: Session, payload: RoleCreate) -> Role:
    try:
        role = Role.model_validate(payload)
        session.add(role)
        session.flush()  # Flush to get the ID before creating UserRole records

        # Create user_roles for this new role for every user
        untrained_proficiency_level = session.exec(select(ProficiencyLevel).where(ProficiencyLevel.code == "untrained")).first()
        proficiency_level_id = untrained_proficiency_level.id if untrained_proficiency_level else None
        for user in session.exec(select(User)).all():
            session.add(UserRole(user_id=user.id, role_id=role.id, proficiency_level_id=proficiency_level_id))

        session.commit()
        session.refresh(role)
        return role
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("Role creation violates a constraint") from e

# =============================
# CREATE USER WITH USER ROLES
# =============================
def create_user_with_user_roles(session: Session, payload: UserCreate) -> User:
    try:
        user = User.model_validate(payload)
        session.add(user)
        session.flush()  # Flush to get the ID before creating UserRole records

        # Create user_roles for this new user for every role
        untrained_proficiency_level = session.exec(select(ProficiencyLevel).where(ProficiencyLevel.code == "untrained")).first()
        proficiency_level_id = untrained_proficiency_level.id if untrained_proficiency_level else None
        for role in session.exec(select(Role)).all():
            session.add(UserRole(user_id=user.id, role_id=role.id, proficiency_level_id=proficiency_level_id))

        session.commit()
        session.refresh(user)
        return user
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("User creation violates a constraint") from e

# =============================
# CREATE TEAM USER FOR TEAM
# =============================
def create_team_user_for_team(session: Session, payload: TeamUserCreate, team: Team) -> TeamUser:
    new_team_user = TeamUser(team_id=team.id, user_id=payload.user_id, is_active=payload.is_active)
    try:
        session.add(new_team_user)
        session.commit()
        session.refresh(new_team_user)
        return new_team_user
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("Team user creation violates a constraint") from e

# =============================
# UPDATE TEAM USER
# =============================
def update_team_user(session: Session, payload: TeamUserUpdate, team_user: TeamUser) -> TeamUserPublic:
    try:
        payload_dict = require_non_empty_payload(payload)
        for key, value in payload_dict.items():
            setattr(team_user, key, value)
        session.commit()
        session.refresh(team_user)
        return TeamUserPublic.from_objects(team_user=team_user, team=team_user.team, user=team_user.user)
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("Team user update violates a constraint") from e

# =============================
# UPDATE USER ROLE
# =============================
def update_user_role(session: Session, payload: UserRoleUpdate, user_role: UserRole) -> UserRolePublic:
    try:
        payload_dict = require_non_empty_payload(payload)
        for key, value in payload_dict.items():
            setattr(user_role, key, value)
        session.commit()
        session.refresh(user_role)
        return UserRolePublic.from_objects(user_role=user_role, user=user_role.user, role=user_role.role, proficiency_level=user_role.proficiency_level)
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("User role update violates a constraint") from e

# =============================
# GET SCHEDULE GRID FROM SCHEDULE
# =============================
def get_schedule_grid_from_schedule(session: Session, schedule: Schedule) -> ScheduleGridPublic:
    schedule_grid_events = []
    for event in schedule.events:
        unavailable_users = select_unavailable_users_for_event(session=session, event_id=event.id)
        unavailable_users = [] if unavailable_users is None else unavailable_users
        schedule_grid_events.append(
            EventWithAssignmentsAndAvailabilityPublic(
                event=EventPublic.from_objects(
                    event=event, schedule=schedule, event_type=event.event_type, team=event.team
                ),
                event_assignments=[
                    EventAssignmentEmbeddedPublic.from_objects(
                        event_assignment=ea, role=ea.role, assigned_user=ea.assigned_user,
                    ) for ea in event.event_assignments
                ],
                availability=[
                    UserUnavailablePeriodEmbeddedPublic(
                        user_first_name=ua.user.first_name, user_last_name=ua.user.last_name,
                    ) for ua in unavailable_users
                ],
            )
        )
    return ScheduleGridPublic.from_objects(schedule=schedule, events=schedule_grid_events)

# =============================
# CREATE EVENT WITH DEFAULT ASSIGNMENT SLOTS
# =============================
def create_event_with_default_assignment_slots(session: Session, payload: EventCreate, schedule: Schedule) -> Event:
    new_event = Event(schedule_id=schedule.id, **payload.model_dump())
    active_roles = session.exec(select(Role).where(Role.is_active == True)).all()
    for role in active_roles:
        # TODO: Set is_applicable and requirement_level
        new_event.event_assignments.append(EventAssignment(event_id=new_event.id, role_id=role.id))
    try:
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        return new_event
    except IntegrityError as e:
        session.rollback()
        if "event_check_time_range" in str(e):
            raise CheckConstraintError("Start time must be before end time") from e
        raise ConflictError("Event creation violates a constraint") from e

# =============================
# GET EVENT ASSIGNMENTS FROM EVENT
# =============================
def get_event_assignments_from_event(event: Event) -> list[EventAssignmentPublic]:
    event_assignments_public = []
    for ea in event.event_assignments:
        assigned_user = ea.assigned_user
        proficiency_level = None
        if assigned_user:
            proficiency_level = next((ur.proficiency_level for ur in assigned_user.user_roles if ur.role_id == ea.role_id), None)
        
        event_assignments_public.append(
            EventAssignmentPublic.from_objects(
                event_assignment=ea,
                event=event,
                role=ea.role,
                event_type=event.event_type,
                team=event.team,
                assigned_user=assigned_user,
                proficiency_level=proficiency_level,
            )
        )
    return event_assignments_public

# =============================
# UPDATE EVENT ASSIGNMENT
# =============================
def update_event_assignment(session: Session, payload: EventAssignmentUpdate, event_assignment: EventAssignment) -> EventAssignmentPublic:
    try:
        payload_dict = require_non_empty_payload(payload)
        for key, value in payload_dict.items():
            setattr(event_assignment, key, value)
        session.commit()
        session.refresh(event_assignment)
        proficiency_level = next((ur.proficiency_level for ur in event_assignment.assigned_user.user_roles if ur.role_id == event_assignment.role_id), None)
        return EventAssignmentPublic.from_objects(
            event_assignment=event_assignment,
            event=event_assignment.event,
            role=event_assignment.role,
            event_type=event_assignment.event.event_type,
            team=event_assignment.event.team,
            assigned_user=event_assignment.assigned_user,
            proficiency_level=proficiency_level
        )
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("Event assignment update violates a constraint") from e