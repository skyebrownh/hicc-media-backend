from .roles import Role, RoleCreate, RoleUpdate
from .proficiency_levels import ProficiencyLevel, ProficiencyLevelCreate, ProficiencyLevelUpdate
from .event_types import EventType, EventTypeCreate, EventTypeUpdate
from .teams import Team, TeamCreate, TeamUpdate
from .users import User, UserCreate, UserUpdate
from .team_users import TeamUser, TeamUserCreate, TeamUserUpdate, TeamUserPublic
from .user_roles import UserRole, UserRoleCreate, UserRoleUpdate, UserRolePublic
from .schedules import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleGridPublic
from .events import Event, EventCreate, EventUpdate, EventPublic, EventWithAssignmentsPublic, EventWithAssignmentsAndAvailabilityPublic
from .event_assignments import EventAssignment, EventAssignmentCreate, EventAssignmentUpdate, EventAssignmentPublic, EventAssignmentEmbeddedPublic
from .user_unavailable_periods import UserUnavailablePeriod, UserUnavailablePeriodCreate, UserUnavailablePeriodUpdate, UserUnavailablePeriodPublic, UserUnavailablePeriodEmbeddedPublic

# Rebuild models with forward references after all imports are complete
EventWithAssignmentsPublic.model_rebuild()
EventWithAssignmentsAndAvailabilityPublic.model_rebuild()
ScheduleGridPublic.model_rebuild()