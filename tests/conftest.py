pytest_plugins = ("pytest_asyncio",)

# Shared configurations and fixtures for tests
from contextlib import asynccontextmanager
import asyncio
import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from fastapi import Request

from sqlmodel import create_engine, Session, text
from alembic.config import Config
from alembic import command

from app.main import app
from app.utils.dependencies import get_db_session
from app.utils.helpers import VALID_TABLES
from app.settings import settings

from app.db.models import Role, ProficiencyLevel, EventType, Team, User, TeamUser, UserRole, Schedule, Event, EventAssignment, UserUnavailablePeriod
from tests.utils.constants import (
    DATETIME_2025_01_01, DATETIME_2025_01_02, DATETIME_2025_02_29, DATETIME_2025_03_01, DATETIME_2025_03_31, DATETIME_2025_04_01, DATETIME_2025_05_01, DATETIME_2025_05_02, DATETIME_2025_05_03, DATETIME_2025_05_04,
    USER_ID_1, USER_ID_2, USER_ID_3, USER_ID_4,
    TEAM_ID_1, TEAM_ID_2, TEAM_ID_3, TEAM_ID_4,
    ROLE_ID_1, ROLE_ID_2, ROLE_ID_3, ROLE_ID_4,
    PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2, PROFICIENCY_LEVEL_ID_3, PROFICIENCY_LEVEL_ID_4,
    SCHEDULE_ID_1, SCHEDULE_ID_2, SCHEDULE_ID_3,
    EVENT_TYPE_ID_1, EVENT_TYPE_ID_2, EVENT_TYPE_ID_3, EVENT_TYPE_ID_4,
    EVENT_ID_1, EVENT_ID_2, EVENT_ID_3,
    EVENT_ASSIGNMENT_ID_1, EVENT_ASSIGNMENT_ID_2, EVENT_ASSIGNMENT_ID_3,
    USER_UNAVAILABLE_PERIOD_ID_1, USER_UNAVAILABLE_PERIOD_ID_2, USER_UNAVAILABLE_PERIOD_ID_3, USER_UNAVAILABLE_PERIOD_ID_4,
    USER_UNAVAILABLE_PERIOD_ID_5, USER_UNAVAILABLE_PERIOD_ID_6, USER_UNAVAILABLE_PERIOD_ID_7, USER_UNAVAILABLE_PERIOD_ID_8,
)

TEST_SCHEMA = "test_schema"

# =============================
# LIFESPAN OVERRIDE
# =============================
# Define a no-op lifespan to disable startup/shutdown events during testing
@asynccontextmanager
async def _noop_lifespan(_app):
    yield

# Override the app's lifespan with the no-op lifespan for testing
@pytest.fixture(scope="session", autouse=True)
def disable_app_lifespan():
    """Disable the app's lifespan for testing"""
    app.router.lifespan_context = _noop_lifespan

# =============================
# ASYNC CLIENT FIXTURES
# =============================
# Use a single loop for session-scoped async fixtures to avoid cross-loop issues.
@pytest.fixture(scope="session")
def event_loop():
    """Create and teardown a event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db_engine():
    """Sync engine for testing"""
    engine = create_engine(
        settings.local_test_db_url,
        pool_pre_ping=True,
        connect_args={"options": f"-csearch_path={TEST_SCHEMA}"}
    )
    try:
        yield engine
    finally:
        engine.dispose()

@pytest.fixture(scope="session", autouse=True)
def apply_migrations(test_db_engine):
    """
    Apply migrations to the test database:
    1. Ensure test_schema exists
    2. Run alembic upgrade head against the test DB URL
    """
    with test_db_engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA};"))

    # Run alembic migrations to build schema in test_schema
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", settings.local_test_db_url)
    alembic_config.set_main_option("search_path", TEST_SCHEMA)
    command.upgrade(alembic_config, "head")

@pytest.fixture(scope="function")
def get_test_db_session(test_db_engine):
    """
    Provide a database session for the test database.
    """
    with Session(test_db_engine) as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def async_client(test_db_engine, request):
    """
    Create an async HTTP client for testing with database connection override.
    
    Sets up the app state with the test database engine and overrides the
    get_db_session dependency to use the test engine.
    
    Headers can be customized by using pytest.mark.parametrize with indirect=True.
    Default includes API key. Custom headers override defaults.
    
    Example:
        @pytest.mark.parametrize("async_client", [{"x-api-key": "custom-key"}], indirect=True)
        async def test_with_custom_headers(async_client):
            ...
    """
    # Get custom headers from fixture parameter if parametrized
    # If parametrized with a dict (even empty), use it as-is (allows testing without auth)
    # If not parametrized, use default headers with API key
    default_headers = {"x-api-key": settings.fast_api_key}
    
    if hasattr(request, "param") and isinstance(request.param, dict):
        # Use provided headers as-is (empty dict = no headers for auth testing)
        headers = request.param
    else:
        # Not parametrized, use default headers
        headers = default_headers
    
    # Set app state with test engine (needed for health endpoint and get_db_session)
    app.state.db_engine = test_db_engine
    
    # Override the get_db_session dependency to use test engine
    def get_test_session(request: Request):
        with Session(test_db_engine) as session:
            yield session

    app.dependency_overrides[get_db_session] = get_test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        yield client
    
    # Clean up dependency override after test
    app.dependency_overrides.clear()

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
# SHARED DATA FIXTURES
# =============================
# These fixtures provide standardized test data that can be reused across test files.
# Tests can use slicing/indexing to get subsets as needed (e.g., test_users_data[:2])

@pytest.fixture
def test_users_data():
    """Standard fixture providing array of test user data"""
    user_1 = User(id=USER_ID_1, first_name="Alice", last_name="Smith", phone="555-1111", email="alice@example.com")
    user_2 = User(id=USER_ID_2, first_name="Bob", last_name="Jones", phone="555-2222", email="bob@example.com")
    user_3 = User(id=USER_ID_3, first_name="Carol", last_name="Lee", phone="555-3333", email=None)
    user_4 = User(id=USER_ID_4, first_name="Another", last_name="User", phone="555-5555", email="another@example.com")
    return [user_1, user_2, user_3, user_4]

@pytest.fixture
def test_teams_data():
    """Standard fixture providing array of test team data (4 teams)"""
    team_1 = Team(id=TEAM_ID_1, name="Team 1", code="team_1")
    team_2 = Team(id=TEAM_ID_2, name="Team 2", code="team_2")
    team_3 = Team(id=TEAM_ID_3, name="Team 3", code="team_3")
    team_4 = Team(id=TEAM_ID_4, name="Another Team", code="new_team")
    return [team_1, team_2, team_3, team_4]

@pytest.fixture
def test_roles_data():
    """Standard fixture providing array of test role data"""
    role_1 = Role(id=ROLE_ID_1, name="ProPresenter", order=10, code="propresenter")
    role_2 = Role(id=ROLE_ID_2, name="Sound", order=20, code="sound")
    role_3 = Role(id=ROLE_ID_3, name="Lighting", order=30, code="lighting")
    role_4 = Role(id=ROLE_ID_4, name="New Role", order=4, code="new_role")
    role_5 = Role(id=ROLE_ID_4, name="Another Role", order=5, code="another_role")
    return [role_1, role_2, role_3, role_4, role_5]

@pytest.fixture
def test_proficiency_levels_data():
    """Standard fixture providing array of test proficiency_level data"""
    pl_1 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_1, name="Novice", code="novice", rank=3, is_assignable=True)
    pl_2 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_2, name="Proficient", code="proficient", rank=4, is_assignable=True)
    pl_3 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_3, name="Untrained", code="untrained", rank=0, is_assignable=True)
    pl_4 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_4, name="New Level", code="new_level", rank=5, is_assignable=False)
    pl_5 = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_4, name="Another Level", code="another_level", rank=5, is_assignable=False)
    return [pl_1, pl_2, pl_3, pl_4, pl_5]

@pytest.fixture
def test_event_types_data():
    """Standard fixture providing array of test event_type data"""
    event_type_1 = EventType(id=EVENT_TYPE_ID_1, name="Service", code="service")
    event_type_2 = EventType(id=EVENT_TYPE_ID_2, name="Rehearsal", code="rehearsal")
    event_type_3 = EventType(id=EVENT_TYPE_ID_3, name="New Type", code="new_type")
    event_type_4 = EventType(id=EVENT_TYPE_ID_4, name="Another Type", code="another_type")
    return [event_type_1, event_type_2, event_type_3, event_type_4]

@pytest.fixture
def test_team_users_data():
    """Standard fixture providing array of test team_user data"""
    team_user_1 = TeamUser(team_id=TEAM_ID_1, user_id=USER_ID_1)
    team_user_2 = TeamUser(team_id=TEAM_ID_1, user_id=USER_ID_2)
    team_user_3 = TeamUser(team_id=TEAM_ID_2, user_id=USER_ID_1)
    team_user_4 = TeamUser(team_id=TEAM_ID_2, user_id=USER_ID_3)
    return [team_user_1, team_user_2, team_user_3, team_user_4]

@pytest.fixture
def test_user_roles_data():
    """Standard fixture providing array of test user_role data"""
    user_role_1 = UserRole(user_id=USER_ID_1, role_id=ROLE_ID_1, proficiency_level_id=PROFICIENCY_LEVEL_ID_1)
    user_role_2 = UserRole(user_id=USER_ID_1, role_id=ROLE_ID_2, proficiency_level_id=PROFICIENCY_LEVEL_ID_2)
    user_role_3 = UserRole(user_id=USER_ID_2, role_id=ROLE_ID_1, proficiency_level_id=PROFICIENCY_LEVEL_ID_1)
    user_role_4 = UserRole(user_id=USER_ID_3, role_id=ROLE_ID_2, proficiency_level_id=PROFICIENCY_LEVEL_ID_1)
    return [user_role_1, user_role_2, user_role_3, user_role_4]

@pytest.fixture
def test_user_unavailable_periods_data():
    """Standard fixture providing array of test user_unavailable_period data"""
    uup_1 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_1, user_id=USER_ID_1, starts_at=DATETIME_2025_02_29, ends_at=DATETIME_2025_03_01)
    uup_2 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_2, user_id=USER_ID_1, starts_at=DATETIME_2025_01_01, ends_at=DATETIME_2025_01_02)
    uup_3 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_3, user_id=USER_ID_1, starts_at=DATETIME_2025_03_31, ends_at=DATETIME_2025_04_01)
    uup_4 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_4, user_id=USER_ID_2, starts_at=DATETIME_2025_02_29, ends_at=DATETIME_2025_03_01)
    uup_5 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_5, user_id=USER_ID_2, starts_at=DATETIME_2025_01_01, ends_at=DATETIME_2025_01_02)
    uup_6 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_6, user_id=USER_ID_2, starts_at=DATETIME_2025_03_31, ends_at=DATETIME_2025_04_01)
    uup_7 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_7, user_id=USER_ID_1, starts_at=DATETIME_2025_05_01, ends_at=DATETIME_2025_05_02)
    uup_8 = UserUnavailablePeriod(id=USER_UNAVAILABLE_PERIOD_ID_8, user_id=USER_ID_2, starts_at=DATETIME_2025_05_01, ends_at=DATETIME_2025_05_02)
    return [uup_1, uup_2, uup_3, uup_4, uup_5, uup_6, uup_7, uup_8]

@pytest.fixture
def test_schedules_data():
    """Standard fixture providing array of test schedule data"""
    schedule_1 = Schedule(id=SCHEDULE_ID_1, month=1, year=2025, notes="First schedule")
    schedule_2 = Schedule(id=SCHEDULE_ID_2, month=5, year=2025, notes="Second schedule")
    schedule_3 = Schedule(id=SCHEDULE_ID_3, month=5, year=2025, notes=None)
    return [schedule_1, schedule_2, schedule_3]

@pytest.fixture
def test_events_data():
    """Standard fixture providing array of test event data"""
    event_1 = Event(id=EVENT_ID_1, schedule_id=SCHEDULE_ID_2, event_type_id=EVENT_TYPE_ID_1, starts_at=DATETIME_2025_05_01, ends_at=DATETIME_2025_05_02)
    event_2 = Event(id=EVENT_ID_2, schedule_id=SCHEDULE_ID_2, event_type_id=EVENT_TYPE_ID_1, starts_at=DATETIME_2025_05_02, ends_at=DATETIME_2025_05_03)
    event_3 = Event(id=EVENT_ID_3, schedule_id=SCHEDULE_ID_2, event_type_id=EVENT_TYPE_ID_1, starts_at=DATETIME_2025_05_03, ends_at=DATETIME_2025_05_04)
    return [event_1, event_2, event_3]

@pytest.fixture
def test_event_assignments_data():
    """Standard fixture providing array of test event_assignment data"""
    event_assignment_1 = EventAssignment(id=EVENT_ASSIGNMENT_ID_1, event_id=EVENT_ID_1, role_id=ROLE_ID_1, is_applicable=True, assigned_user_id=USER_ID_1)
    event_assignment_2 = EventAssignment(id=EVENT_ASSIGNMENT_ID_2, event_id=EVENT_ID_1, role_id=ROLE_ID_2, is_applicable=True)
    event_assignment_3 = EventAssignment(id=EVENT_ASSIGNMENT_ID_3, event_id=EVENT_ID_2, role_id=ROLE_ID_1, is_applicable=True)
    return [event_assignment_1, event_assignment_2, event_assignment_3]