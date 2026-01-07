from uuid import UUID, uuid4
from pydantic import ConfigDict
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, ForeignKey, UniqueConstraint, TIMESTAMP
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.db.models import User, Role, ProficiencyLevel

class UserRoleBase(SQLModel):
    proficiency_level_id: UUID = Field(sa_column=Column(ForeignKey("proficiency_levels.id"), index=True, nullable=False))

class UserRole(UserRoleBase, table=True):
    __tablename__ = "user_roles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False))
    role_id: UUID = Field(sa_column=Column(ForeignKey("roles.id", ondelete="CASCADE"), index=True, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    )

    # Relationships
    user: "User" = Relationship(back_populates="user_roles")
    role: "Role" = Relationship(back_populates="user_roles")
    proficiency_level: "ProficiencyLevel" = Relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="user_role_ukey"),
    )

class UserRoleUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")
    # user_role.user_id + user_role.role_id is used to update the user role
    proficiency_level_id: UUID | None = None

class UserRolePublic(UserRoleBase):
    id: UUID
    user_id: UUID
    role_id: UUID
    proficiency_level_id: UUID
    # join fields
    user_first_name: str
    user_last_name: str
    user_email: str | None
    user_phone: str
    user_is_active: bool
    role_name: str
    role_description: str | None
    role_order: int
    role_is_active: bool
    role_code: str
    proficiency_level_name: str
    proficiency_level_rank: int | None
    proficiency_level_is_assignable: bool
    proficiency_level_is_active: bool
    proficiency_level_code: str
    
    @classmethod
    def from_objects(
        cls,
        user_role: "UserRole",
        user: "User",
        role: "Role",
        proficiency_level: "ProficiencyLevel",
    ):
        """Create a UserRolePublic from the related objects."""
        return cls(
            id=user_role.id,
            user_id=user_role.user_id,
            role_id=user_role.role_id,
            proficiency_level_id=user_role.proficiency_level_id,
            user_first_name=user.first_name,
            user_last_name=user.last_name,
            user_email=user.email,
            user_phone=user.phone,
            user_is_active=user.is_active,
            role_name=role.name,
            role_description=role.description,
            role_order=role.order,
            role_is_active=role.is_active,
            role_code=role.code,
            proficiency_level_name=proficiency_level.name,
            proficiency_level_rank=proficiency_level.rank,
            proficiency_level_is_assignable=proficiency_level.is_assignable,
            proficiency_level_is_active=proficiency_level.is_active,
            proficiency_level_code=proficiency_level.code,
        )