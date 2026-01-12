import pytest
import pytest_asyncio
from sqlmodel import text

from app.utils.helpers import VALID_TABLES
from app.db.models import Role, ProficiencyLevel, EventType, Team, User, TeamUser, UserRole, Schedule, Event, EventAssignment, UserUnavailablePeriod

@pytest_asyncio.fixture(autouse=True, scope="function")
async def truncate_tables(test_db_engine):
    """
    Truncate tables before each test to keep state isolated without recreating schema.
    Assumes search_path=test_schema so unqualified table names resolve correctly.
    """
    truncate_sql = f"""
    TRUNCATE TABLE
        {', '.join(VALID_TABLES)}
    RESTART IDENTITY CASCADE;
    """

    with test_db_engine.begin() as conn:
        conn.execute(text(truncate_sql))
    yield

# =============================
# SEED HELPER FIXTURES
# =============================
@pytest.fixture
def seed_roles(get_test_db_session):
    def _seed_roles(roles: list[Role]):
        if roles:
            get_test_db_session.add_all(roles)
        get_test_db_session.commit()
    return _seed_roles

@pytest.fixture
def seed_proficiency_levels(get_test_db_session):
    def _seed_proficiency_levels(proficiency_levels: list[ProficiencyLevel]):
        if proficiency_levels:
            get_test_db_session.add_all(proficiency_levels)
        get_test_db_session.commit()
    return _seed_proficiency_levels

@pytest.fixture
def seed_event_types(get_test_db_session):
    def _seed_event_types(event_types: list[EventType]):
        if event_types:
            get_test_db_session.add_all(event_types)
        get_test_db_session.commit()
    return _seed_event_types

@pytest.fixture
def seed_users(get_test_db_session):
    def _seed_users(users: list[User]):
        if users:
            get_test_db_session.add_all(users)
        get_test_db_session.commit()
    return _seed_users

@pytest.fixture
def seed_teams(get_test_db_session):
    def _seed_teams(teams: list[Team]):
        if teams:
            get_test_db_session.add_all(teams)
        get_test_db_session.commit()
    return _seed_teams

@pytest.fixture
def seed_user_roles(get_test_db_session):
    def _seed_user_roles(user_roles: list[UserRole]):
        if user_roles:
            get_test_db_session.add_all(user_roles)
        get_test_db_session.commit()
    return _seed_user_roles

@pytest.fixture
def seed_team_users(get_test_db_session):
    def _seed_team_users(team_users: list[TeamUser]):
        if team_users:
            get_test_db_session.add_all(team_users)
        get_test_db_session.commit()
    return _seed_team_users

@pytest.fixture
def seed_schedules(get_test_db_session):
    def _seed_schedules(schedules: list[Schedule]):
        if schedules:
            get_test_db_session.add_all(schedules)
        get_test_db_session.commit()
    return _seed_schedules

@pytest.fixture
def seed_events(get_test_db_session):
    def _seed_events(events: list[Event]):
        if events:
            get_test_db_session.add_all(events)
        get_test_db_session.commit()
    return _seed_events

@pytest.fixture
def seed_event_assignments(get_test_db_session):
    def _seed_event_assignments(event_assignments: list[EventAssignment]):
        if event_assignments:
            get_test_db_session.add_all(event_assignments)
        get_test_db_session.commit()
    return _seed_event_assignments

@pytest.fixture
def seed_user_unavailable_periods(get_test_db_session):
    def _seed_user_unavailable_periods(user_unavailable_periods: list[UserUnavailablePeriod]):
        if user_unavailable_periods:
            get_test_db_session.add_all(user_unavailable_periods)
        get_test_db_session.commit()
    return _seed_user_unavailable_periods