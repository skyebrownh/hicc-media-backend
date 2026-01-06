import pytest
from app.db.models import Role, ProficiencyLevel, EventType, Team, User, TeamUser, UserRole, Schedule, Event, EventAssignment, UserUnavailablePeriod
# Test data fixtures are now in tests/conftest.py and available to all tests

# =============================
# CONDITIONAL SEEDING HELPER
# =============================
def conditional_seed(indices, data, seed_func):
    """Conditionally seed data only if indices are provided (non-empty list)"""
    if indices:
        items = [data[i] for i in indices]
        seed_func(items)

# =============================
# SEED HELPER FIXTURES
# =============================
@pytest.fixture
def seed_roles(get_test_db_session):
    """Helper fixture to seed roles in the database"""
    def _seed_roles(roles: list[Role]):
        if roles:
            get_test_db_session.add_all(roles)
        get_test_db_session.commit()
    return _seed_roles

@pytest.fixture
def seed_proficiency_levels(get_test_db_session):
    """Helper fixture to seed proficiency_levels in the database"""
    def _seed_proficiency_levels(proficiency_levels: list[ProficiencyLevel]):
        if proficiency_levels:
            get_test_db_session.add_all(proficiency_levels)
        get_test_db_session.commit()
    return _seed_proficiency_levels

@pytest.fixture
def seed_event_types(get_test_db_session):
    """Helper fixture to seed event_types in the database"""
    def _seed_event_types(event_types: list[EventType]):
        if event_types:
            get_test_db_session.add_all(event_types)
        get_test_db_session.commit()
    return _seed_event_types

@pytest.fixture
def seed_users(get_test_db_session):
    """Helper fixture to seed users in the database"""
    def _seed_users(users: list[User]):
        if users:
            get_test_db_session.add_all(users)
        get_test_db_session.commit()
    return _seed_users

@pytest.fixture
def seed_teams(get_test_db_session):
    """Helper fixture to seed teams in the database"""
    def _seed_teams(teams: list[Team]):
        if teams:
            get_test_db_session.add_all(teams)
        get_test_db_session.commit()
    return _seed_teams

@pytest.fixture
def seed_user_roles(get_test_db_session):
    """Helper fixture to seed user_roles in the database"""
    def _seed_user_roles(user_roles: list[UserRole]):
        if user_roles:
            get_test_db_session.add_all(user_roles)
        get_test_db_session.commit()
    return _seed_user_roles

@pytest.fixture
def seed_team_users(get_test_db_session):
    """Helper fixture to seed team_users in the database"""
    def _seed_team_users(team_users: list[TeamUser]):
        if team_users:
            get_test_db_session.add_all(team_users)
        get_test_db_session.commit()
    return _seed_team_users

@pytest.fixture
def seed_schedules(get_test_db_session):
    """Helper fixture to seed schedules in the database"""
    def _seed_schedules(schedules: list[Schedule]):
        if schedules:
            get_test_db_session.add_all(schedules)
        get_test_db_session.commit()
    return _seed_schedules

@pytest.fixture
def seed_events(get_test_db_session):
    """Helper fixture to seed events in the database"""
    def _seed_events(events: list[Event]):
        if events:
            get_test_db_session.add_all(events)
        get_test_db_session.commit()
    return _seed_events

@pytest.fixture
def seed_event_assignments(get_test_db_session):
    """Helper fixture to seed event_assignments in the database"""
    def _seed_event_assignments(event_assignments: list[EventAssignment]):
        if event_assignments:
            get_test_db_session.add_all(event_assignments)
        get_test_db_session.commit()
    return _seed_event_assignments

@pytest.fixture
def seed_user_unavailable_periods(get_test_db_session):
    """Helper fixture to seed user_unavailable_periods in the database"""
    def _seed_user_unavailable_periods(user_unavailable_periods: list[UserUnavailablePeriod]):
        if user_unavailable_periods:
            get_test_db_session.add_all(user_unavailable_periods)
        get_test_db_session.commit()
    return _seed_user_unavailable_periods