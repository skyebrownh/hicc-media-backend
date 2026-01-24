import pytest

from app.db.models import Role, ProficiencyLevel, EventType, Team, User, TeamUser, UserRole, Schedule, Event, EventAssignment, UserUnavailablePeriod
from tests.utils.constants import *

# =============================
# SHARED DATA FIXTURES
# =============================
# These fixtures provide standardized test data that can be reused across test files.
# Tests can use slicing/indexing to get subsets as needed (e.g., test_users_data[:2])

@pytest.fixture
def test_users_data():
    user_1 = User(id=USER_ID_1, first_name="Alice", last_name="Smith", phone="+12345551111", email="alice@example.com")
    user_2 = User(id=USER_ID_2, first_name="Bob", last_name="Jones", phone="+12345552222", email="bob@example.com")
    user_3 = User(id=USER_ID_3, first_name="Carol", last_name="Lee", phone="+12345553333", email=None)
    return [user_1, user_2, user_3]

@pytest.fixture
def test_teams_data():
    team_1 = Team(id=TEAM_ID_1, name="Team 1", code="team_1")
    team_2 = Team(id=TEAM_ID_2, name="Team 2", code="team_2")
    team_3 = Team(id=TEAM_ID_3, name="Another Team", code="new_team")
    return [team_1, team_2, team_3]

@pytest.fixture
def test_roles_data():
    role_1 = Role(id=ROLE_ID_1, name="ProPresenter", order=10, code="propresenter")
    role_2 = Role(id=ROLE_ID_2, name="Sound", order=20, code="sound")
    role_3 = Role(id=ROLE_ID_3, name="New Role", order=4, code="new_role")
    return [role_1, role_2, role_3]

@pytest.fixture
def test_proficiency_levels_data():
    pl_1 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_1, name="Novice", code="novice", rank=3, is_assignable=True)
    pl_2 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_2, name="Proficient", code="proficient", rank=4, is_assignable=True)
    pl_3 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_3, name="Untrained", code="untrained", rank=0, is_assignable=True)
    return [pl_1, pl_2, pl_3]

@pytest.fixture
def test_event_types_data():
    event_type_1 = EventType(id=EVENT_TYPE_ID_1, name="Service", code="service")
    event_type_2 = EventType(id=EVENT_TYPE_ID_2, name="Rehearsal", code="rehearsal")
    event_type_3 = EventType(id=EVENT_TYPE_ID_3, name="New Type", code="new_type")
    return [event_type_1, event_type_2, event_type_3]

@pytest.fixture
def test_team_users_data():
    team_user_1 = TeamUser(team_id=TEAM_ID_1, user_id=USER_ID_1)
    team_user_2 = TeamUser(team_id=TEAM_ID_1, user_id=USER_ID_2)
    team_user_3 = TeamUser(team_id=TEAM_ID_2, user_id=USER_ID_1)
    return [team_user_1, team_user_2, team_user_3]

@pytest.fixture
def test_user_roles_data():
    user_role_1 = UserRole(user_id=USER_ID_1, role_id=ROLE_ID_1, proficiency_level_id=PROFICIENCY_LEVEL_ID_1)
    user_role_2 = UserRole(user_id=USER_ID_1, role_id=ROLE_ID_2, proficiency_level_id=PROFICIENCY_LEVEL_ID_2)
    user_role_3 = UserRole(user_id=USER_ID_2, role_id=ROLE_ID_1, proficiency_level_id=PROFICIENCY_LEVEL_ID_1)
    return [user_role_1, user_role_2, user_role_3]

@pytest.fixture
def test_user_unavailable_periods_data():
    uup_1 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_1, user_id=USER_ID_1, starts_at=DATETIME_2024_02_29, ends_at=DATETIME_2025_03_01)
    uup_2 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_2, user_id=USER_ID_1, starts_at=DATETIME_2025_05_01, ends_at=DATETIME_2025_05_02)
    uup_3 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_3, user_id=USER_ID_2, starts_at=DATETIME_2025_05_01, ends_at=DATETIME_2025_05_02)
    return [uup_1, uup_2, uup_3]

@pytest.fixture
def test_schedules_data():
    schedule_1 = Schedule(id=SCHEDULE_ID_1, month=1, year=2025, notes="First schedule")
    schedule_2 = Schedule(id=SCHEDULE_ID_2, month=5, year=2025, notes="Second schedule")
    return [schedule_1, schedule_2]

@pytest.fixture
def test_events_data():
    event_1 = Event(id=EVENT_ID_1, schedule_id=SCHEDULE_ID_2, event_type_id=EVENT_TYPE_ID_1, starts_at=DATETIME_2025_05_01, ends_at=DATETIME_2025_05_02)
    event_2 = Event(id=EVENT_ID_2, schedule_id=SCHEDULE_ID_2, event_type_id=EVENT_TYPE_ID_1, starts_at=DATETIME_2025_05_02, ends_at=DATETIME_2025_05_03)
    event_3 = Event(id=EVENT_ID_3, schedule_id=SCHEDULE_ID_2, event_type_id=EVENT_TYPE_ID_1, starts_at=DATETIME_2025_05_03, ends_at=DATETIME_2025_05_04, team_id=TEAM_ID_1)
    return [event_1, event_2, event_3]

@pytest.fixture
def test_event_assignments_data():
    event_assignment_1 = EventAssignment(id=EVENT_ASSIGNMENT_ID_1, event_id=EVENT_ID_1, role_id=ROLE_ID_1, is_applicable=True, assigned_user_id=USER_ID_1)
    event_assignment_2 = EventAssignment(id=EVENT_ASSIGNMENT_ID_2, event_id=EVENT_ID_1, role_id=ROLE_ID_2, is_applicable=True)
    event_assignment_3 = EventAssignment(id=EVENT_ASSIGNMENT_ID_3, event_id=EVENT_ID_2, role_id=ROLE_ID_1, is_applicable=True)
    return [event_assignment_1, event_assignment_2, event_assignment_3]

# =============================
# SAMPLE DATA FIXTURES
# =============================
@pytest.fixture
def sample_schedule_with_events(
    test_users_data,
    test_roles_data,
    test_schedules_data,
    test_event_types_data,
    test_events_data,
    test_event_assignments_data,
):
    """Create a sample Schedule with Events and related objects in memory using shared test data."""
    # Get objects from shared fixtures
    event_type = test_event_types_data[0]
    schedule = test_schedules_data[1]
    user_1 = test_users_data[0]
    role_1 = test_roles_data[0]
    role_2 = test_roles_data[1]
    
    # Get events and assignments
    event_1 = test_events_data[0]
    event_2 = test_events_data[1]
    event_3 = test_events_data[2]
    event_assignment_1 = test_event_assignments_data[0]
    event_assignment_2 = test_event_assignments_data[1]
    
    # Set up relationships
    event_1.schedule = schedule
    event_1.event_type = event_type
    event_1.team = None
    
    event_2.schedule = schedule
    event_2.event_type = event_type
    event_2.team = None
    
    event_3.schedule = schedule
    event_3.event_type = event_type
    event_3.team = None
    
    event_assignment_1.event = event_1
    event_assignment_1.role = role_1
    event_assignment_1.assigned_user = user_1
    
    event_assignment_2.event = event_1
    event_assignment_2.role = role_2
    event_assignment_2.assigned_user = None
    
    # Set up event assignments lists
    event_1.event_assignments = [event_assignment_1, event_assignment_2]
    event_2.event_assignments = []
    event_3.event_assignments = []
    
    schedule.events = [event_1, event_2, event_3]
    
    return schedule

@pytest.fixture
def sample_event_with_assignments(sample_schedule_with_events):
    """Create a sample Event with assignments in memory."""
    return sample_schedule_with_events.events[0]

@pytest.fixture
def sample_schedule_with_availability(
    sample_schedule_with_events,
    test_users_data,
    test_user_unavailable_periods_data,
):
    """Create a sample Schedule with events that have availability information."""
    schedule = sample_schedule_with_events
    
    # Get users and unavailable periods from shared fixtures
    user_1 = test_users_data[0]
    user_2 = test_users_data[1]
    unavailable_period_1 = test_user_unavailable_periods_data[1]  # May 1-2 for user 1
    unavailable_period_2 = test_user_unavailable_periods_data[2]  # May 1-2 for user 2
    
    # Set up user relationships
    unavailable_period_1.user = user_1
    unavailable_period_2.user = user_2
    
    # Set availability on first event
    # Note: This assumes event.availability exists as a relationship or attribute
    schedule.events[0].availability = [unavailable_period_1, unavailable_period_2]
    schedule.events[1].availability = []
    schedule.events[2].availability = []
    
    return schedule