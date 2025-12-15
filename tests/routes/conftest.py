import pytest_asyncio
from tests.utils.helpers import insert_dates, insert_users, insert_user_dates, insert_teams

# =============================
# SEED HELPER FIXTURES
# =============================
@pytest_asyncio.fixture
async def seed_dates(test_db_pool):
    """Helper fixture to seed dates in the database"""
    async def _seed_dates(dates):
        if dates:
            async with test_db_pool.acquire() as conn:
                query = insert_dates(dates)
                if query:
                    await conn.execute(query)
    return _seed_dates

@pytest_asyncio.fixture
async def seed_users(test_db_pool):
    """Helper fixture to seed users in the database"""
    async def _seed_users(users: list[dict]):
        if users:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_users(users))
    return _seed_users

@pytest_asyncio.fixture
async def seed_user_dates(test_db_pool):
    """Helper fixture to seed user_dates in the database"""
    async def _seed_user_dates(user_dates: list[dict]):
        if user_dates:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_user_dates(user_dates))
    return _seed_user_dates

@pytest_asyncio.fixture
async def seed_teams(test_db_pool):
    """Helper fixture to seed teams in the database"""
    async def _seed_teams(teams: list[dict]):
        if teams:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_teams(teams))
    return _seed_teams
