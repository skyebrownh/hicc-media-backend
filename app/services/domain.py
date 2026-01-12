from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.db.models import Role, User, UserRole, ProficiencyLevel, RoleCreate, RoleUpdate
from app.utils.helpers import require_non_empty_payload
from app.utils.exceptions import ConflictError

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

def update_role(session: Session, payload: RoleUpdate, role: Role):
    try:
        payload_dict = require_non_empty_payload(payload)
        for key, value in payload_dict.items():
            setattr(role, key, value)

        session.commit()
        session.refresh(role)
        return role
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("Role update violates a constraint") from e