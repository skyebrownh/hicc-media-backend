pytest_plugins = ("pytest_asyncio",)

# Shared configurations and fixtures for tests
from contextlib import asynccontextmanager
import asyncio
import pytest
import pytest_asyncio
import asyncpg
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from fastapi import Request
from app.main import app
from app.db.database import get_db_connection
from app.settings import settings

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
    app.router.lifespan_context = _noop_lifespan

# =============================
# ASYNC CLIENT FIXTURES
# =============================
# Use a single loop for session-scoped async fixtures to avoid cross-loop issues.
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Apply schema once per session on the same loop pytest-asyncio uses
@pytest_asyncio.fixture(scope="session", autouse=True)
async def ensure_schema():
    schema_sql = Path("tests/test_schema.sql").read_text()
    conn = await asyncpg.connect(settings.local_test_db_url)
    try:
        await conn.execute(schema_sql)
    finally:
        await conn.close()


# Fixture to create and teardown a test database pool, session-scoped
@pytest_asyncio.fixture(scope="session")
async def test_db_pool(ensure_schema):
    pool = await asyncpg.create_pool(
        settings.local_test_db_url,
        min_size=1,
        max_size=5,
        # Keep every pooled connection pinned to test_schema.
        server_settings={"search_path": "test_schema"},
        init=lambda conn: conn.execute("SET search_path TO test_schema;"),
    )

    yield pool
    await pool.close()


# Fixture to provide an async HTTP client for testing
@pytest_asyncio.fixture(scope="function")
async def async_client(test_db_pool):
    """
    Create an async HTTP client for testing with database connection override.
    
    Sets up the app state with the test database pool and overrides the
    get_db_connection dependency to use the test pool.
    """
    headers = {"x-api-key": settings.fast_api_key}
    
    # Set app state with test pool (needed for health endpoint and get_db_connection)
    app.state.db_pool = test_db_pool
    
    # Override the get_db_connection dependency to use test pool
    async def get_test_db_connection(request: Request):
        async with test_db_pool.acquire() as conn:
            yield conn
    
    app.dependency_overrides[get_db_connection] = get_test_db_connection

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        yield client
    
    # Clean up dependency override after test
    app.dependency_overrides.clear()


# Truncate tables before each test to keep state isolated without recreating schema/pool
@pytest_asyncio.fixture(autouse=True, scope="function")
async def truncate_tables(test_db_pool):
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            TRUNCATE TABLE
                user_dates,
                schedule_date_roles,
                schedule_dates,
                schedules,
                dates,
                team_users,
                user_roles,
                users,
                teams,
                schedule_date_types,
                media_roles,
                proficiency_levels
            RESTART IDENTITY CASCADE;
            """
        )
    yield