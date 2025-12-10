pytest_plugins = ("pytest_asyncio",)

# Shared configurations and fixtures for tests
from contextlib import asynccontextmanager
import pytest
import pytest_asyncio
import asyncpg
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db_pool
from app.utils.env import FAST_API_KEY, LOCAL_TEST_DB_URL
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
# ASYNC CLIENT FIXTURE
# =============================
# Fixture to provide an async HTTP client for testing
@pytest_asyncio.fixture(scope="function")
async def async_client():
    # Load schema SQL file
    schema_sql = Path("tests/test_schema.sql").read_text()

    # Ensure every connection uses the test schema (falls back to public if needed)
    pool = await asyncpg.create_pool(
        LOCAL_TEST_DB_URL,
        min_size=1,
        max_size=5,
        # Reset test schema
        init=lambda conn: conn.execute(schema_sql)
    )

    headers = {"x-api-key": FAST_API_KEY}
    # Override the get_db_pool dependency to use the test database pool
    app.dependency_overrides[get_db_pool] = lambda: pool

    # Create an AsyncClient for testing
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        yield client

    await pool.close()
