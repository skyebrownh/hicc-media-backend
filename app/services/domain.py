from typing import Type
from sqlmodel import Session, select, SQLModel
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    Role, User, UserRole, ProficiencyLevel, RoleCreate, UserCreate, 
    Schedule, EventPublic, ScheduleGridPublic,
    EventWithAssignmentsAndAvailabilityPublic, 
    EventAssignmentEmbeddedPublic, 
    UserUnavailablePeriodEmbeddedPublic)
from app.utils.helpers import require_non_empty_payload
from app.utils.exceptions import ConflictError, CheckConstraintError
from app.services.queries import select_unavailable_users_for_event

# =============================
# CREATE OBJECT
# =============================
def create_object(session: Session, payload: SQLModel, model: Type[SQLModel], check_constraint: str | None = None):
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
def update_object(session: Session, payload: SQLModel, object: SQLModel):
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
def create_role_with_user_roles(session: Session, payload: RoleCreate):
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
def create_user_with_user_roles(session: Session, payload: UserCreate):
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
# GET SCHEDULE GRID FROM SCHEDULE
# =============================
def get_schedule_grid_from_schedule(session: Session, schedule: Schedule):
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