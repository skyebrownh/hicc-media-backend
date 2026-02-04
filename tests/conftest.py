pytest_plugins = ("pytest_asyncio","tests.fixtures.data_fixtures","tests.fixtures.seed_fixtures")

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
from app.utils.dependencies import (
    get_db_session,
    require_admin,
    verify_clerk_token
)
from app.settings import settings

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
# BYPASS ADMIN AUTH
# =============================
@pytest.fixture(scope="session", autouse=True)
def bypass_auth():
    """Bypass authentication for testing"""
    app.dependency_overrides[verify_clerk_token] = lambda: {
        "sub": "test_user",
        "public_metadata": {"role": "admin"}
    }
    app.dependency_overrides[require_admin] = lambda: None
    yield
    app.dependency_overrides.clear()

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
    def get_test_session(_: Request):
        with Session(test_db_engine) as session:
            yield session

    app.dependency_overrides[get_db_session] = get_test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        yield client
    
    # Remove only the session override so auth bypass (from bypass_auth) is preserved for other tests
    app.dependency_overrides.pop(get_db_session, None)