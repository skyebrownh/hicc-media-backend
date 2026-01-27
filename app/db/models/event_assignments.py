from uuid import UUID, uuid4
from pydantic import ConfigDict
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, ForeignKey, UniqueConstraint, Enum as SAEnum, TIMESTAMP
from datetime import datetime, timezone

from app.db.models.enums import RequirementLevel

if TYPE_CHECKING:
    from app.db.models import Event, Role, User, EventType, Team, ProficiencyLevel

class EventAssignmentBase(SQLModel):
    # is_applicable: bool - whether the role is applicable to the event
    is_applicable: bool = Field(default=True)
    # requirement_level: RequirementLevel - importance to fill the role for the event
    requirement_level: RequirementLevel = Field(default=RequirementLevel.required, sa_column=Column(SAEnum(RequirementLevel, name="requirement_level")))
    assigned_user_id: UUID | None = Field(default=None, sa_column=Column(ForeignKey("users.id"), index=True, nullable=True))
    is_active: bool = Field(default=True)

class EventAssignment(EventAssignmentBase, table=True):
    __tablename__ = "event_assignments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(sa_column=Column(ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False))
    role_id: UUID = Field(sa_column=Column(ForeignKey("roles.id"), index=True, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    )

    # Relationships
    event: "Event" = Relationship(back_populates="event_assignments")
    role: "Role" = Relationship()
    assigned_user: "User" = Relationship()

    __table_args__ = (
        UniqueConstraint("event_id", "role_id", name="event_assignment_ukey"),
    )

class EventAssignmentUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")
    # event_assignment.id is used to update the event assignment
    # event_assignment.event_id is not updatable, delete and recreate if needed
    requirement_level: RequirementLevel | None = None
    assigned_user_id: UUID | None = None
    is_active: bool | None = None

class EventAssignmentPublic(EventAssignmentBase):
    id: UUID
    event_id: UUID
    role_id: UUID
    # join fields
    event_title: str | None
    event_starts_at: datetime
    event_ends_at: datetime
    event_notes: str | None
    event_is_active: bool
    event_schedule_id: UUID
    event_schedule_month: int
    event_schedule_year: int
    event_schedule_notes: str | None
    event_schedule_is_active: bool
    event_team_id: UUID | None
    event_team_name: str | None
    event_team_code: str | None
    event_team_is_active: bool | None
    event_type_id: UUID
    event_type_name: str
    event_type_code: str
    event_type_is_active: bool
    role_name: str
    role_description: str | None
    role_order: int
    role_code: str
    role_is_active: bool
    assigned_user_id: UUID | None
    assigned_user_first_name: str | None
    assigned_user_last_name: str | None
    assigned_user_email: str | None
    assigned_user_phone: str | None
    assigned_user_is_active: bool | None
    # from user_roles table
    proficiency_level_id: UUID | None
    proficiency_level_name: str | None
    proficiency_level_rank: int | None
    proficiency_level_is_assignable: bool | None
    proficiency_level_is_active: bool | None
    proficiency_level_code: str | None
    
    @classmethod
    def from_objects(
        cls,
        event_assignment: "EventAssignment",
        event: "Event",
        role: "Role",
        event_type: "EventType",
        team: "Team | None" = None,
        assigned_user: "User | None" = None,
        proficiency_level: "ProficiencyLevel | None" = None,
    ):
        """Create an EventAssignmentPublic from the related objects."""
        return cls(
            id=event_assignment.id,
            event_id=event.id,
            role_id=role.id,
            is_applicable=event_assignment.is_applicable,
            requirement_level=event_assignment.requirement_level,
            assigned_user_id=event_assignment.assigned_user_id,
            is_active=event_assignment.is_active,
            event_title=event.title,
            event_starts_at=event.starts_at,
            event_ends_at=event.ends_at,
            event_notes=event.notes,
            event_is_active=event.is_active,
            event_schedule_id=event.schedule_id,
            event_schedule_month=event.schedule.month,
            event_schedule_year=event.schedule.year,
            event_schedule_notes=event.schedule.notes,
            event_schedule_is_active=event.schedule.is_active,
            event_team_id=getattr(team, "id", None),
            event_team_name=getattr(team, "name", None),
            event_team_code=getattr(team, "code", None),
            event_team_is_active=getattr(team, "is_active", None),
            event_type_id=event_type.id,
            event_type_name=event_type.name,
            event_type_code=event_type.code,
            event_type_is_active=event_type.is_active,
            role_name=role.name,
            role_description=role.description,
            role_order=role.order,
            role_code=role.code,
            role_is_active=role.is_active,
            assigned_user_first_name=getattr(assigned_user, "first_name", None),
            assigned_user_last_name=getattr(assigned_user, "last_name", None),
            assigned_user_email=getattr(assigned_user, "email", None),
            assigned_user_phone=getattr(assigned_user, "phone", None),
            assigned_user_is_active=getattr(assigned_user, "is_active", None),
            proficiency_level_id=getattr(proficiency_level, "id", None),
            proficiency_level_name=getattr(proficiency_level, "name", None),
            proficiency_level_rank=getattr(proficiency_level, "rank", None),
            proficiency_level_is_assignable=getattr(proficiency_level, "is_assignable", None),
            proficiency_level_is_active=getattr(proficiency_level, "is_active", None),
            proficiency_level_code=getattr(proficiency_level, "code", None),
        )

class EventAssignmentEmbeddedPublic(EventAssignmentBase):
    id: UUID
    role_id: UUID
    # join fields
    role_name: str
    role_order: int
    role_code: str
    assigned_user_first_name: str | None
    assigned_user_last_name: str | None
    
    @classmethod
    def from_objects(
        cls,
        event_assignment: "EventAssignment",
        role: "Role",
        assigned_user: "User | None" = None,
    ):
        """Create an EventAssignmentEmbeddedPublic from the related objects."""
        return cls(
            id=event_assignment.id,
            is_applicable=event_assignment.is_applicable,
            requirement_level=event_assignment.requirement_level,
            assigned_user_id=event_assignment.assigned_user_id,
            is_active=event_assignment.is_active,
            role_id=role.id,
            role_name=role.name,
            role_order=role.order,
            role_code=role.code,
            assigned_user_first_name=getattr(assigned_user, "first_name", None),
            assigned_user_last_name=getattr(assigned_user, "last_name", None),
        )