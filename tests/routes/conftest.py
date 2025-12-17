import pytest_asyncio
from tests.utils.helpers import (
    insert_dates, insert_users, insert_user_dates, insert_teams,
    insert_media_roles, insert_proficiency_levels, insert_schedules,
    insert_schedule_date_types, insert_schedule_dates, insert_user_roles,
    insert_team_users, insert_schedule_date_roles
)

# =============================
# CONDITIONAL SEEDING HELPER
# =============================
async def conditional_seed(indices, data, seed_func):
    """Conditionally seed data only if indices are provided (non-empty list)"""
    if indices:
        items = [data[i] for i in indices]
        await seed_func(items)

# =============================
# DATABASE QUERY HELPER
# =============================
async def count_records(test_db_pool, table_name: str, where_clause: str = "") -> int:
    """Helper to count records in a table, optionally with a WHERE clause"""
    async with test_db_pool.acquire() as conn:
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        count = await conn.fetchval(query)
        return count

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

@pytest_asyncio.fixture
async def seed_media_roles(test_db_pool):
    """Helper fixture to seed media_roles in the database"""
    async def _seed_media_roles(media_roles: list[dict]):
        if media_roles:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_media_roles(media_roles))
    return _seed_media_roles

@pytest_asyncio.fixture
async def seed_proficiency_levels(test_db_pool):
    """Helper fixture to seed proficiency_levels in the database"""
    async def _seed_proficiency_levels(proficiency_levels: list[dict]):
        if proficiency_levels:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_proficiency_levels(proficiency_levels))
    return _seed_proficiency_levels

@pytest_asyncio.fixture
async def seed_schedules(test_db_pool):
    """Helper fixture to seed schedules in the database"""
    async def _seed_schedules(schedules: list[dict]):
        if schedules:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_schedules(schedules))
    return _seed_schedules

@pytest_asyncio.fixture
async def seed_schedule_date_types(test_db_pool):
    """Helper fixture to seed schedule_date_types in the database"""
    async def _seed_schedule_date_types(schedule_date_types: list[dict]):
        if schedule_date_types:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_schedule_date_types(schedule_date_types))
    return _seed_schedule_date_types

@pytest_asyncio.fixture
async def seed_schedule_dates(test_db_pool):
    """Helper fixture to seed schedule_dates in the database"""
    async def _seed_schedule_dates(schedule_dates: list[dict]):
        if schedule_dates:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_schedule_dates(schedule_dates))
    return _seed_schedule_dates

@pytest_asyncio.fixture
async def seed_user_roles(test_db_pool):
    """Helper fixture to seed user_roles in the database"""
    async def _seed_user_roles(user_roles: list[dict]):
        if user_roles:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_user_roles(user_roles))
    return _seed_user_roles

@pytest_asyncio.fixture
async def seed_team_users(test_db_pool):
    """Helper fixture to seed team_users in the database"""
    async def _seed_team_users(team_users: list[dict]):
        if team_users:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_team_users(team_users))
    return _seed_team_users

@pytest_asyncio.fixture
async def seed_schedule_date_roles(test_db_pool):
    """Helper fixture to seed schedule_date_roles in the database"""
    async def _seed_schedule_date_roles(schedule_date_roles: list[dict]):
        if schedule_date_roles:
            async with test_db_pool.acquire() as conn:
                await conn.execute(insert_schedule_date_roles(schedule_date_roles))
    return _seed_schedule_date_roles
