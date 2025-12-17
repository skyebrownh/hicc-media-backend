import pytest
import pytest_asyncio
from tests.utils.constants import *
from tests.utils.helpers import (
    insert_dates, insert_users, insert_user_dates, insert_teams,
    insert_media_roles, insert_proficiency_levels, insert_schedules,
    insert_schedule_date_types, insert_schedule_dates, insert_user_roles,
    insert_team_users, insert_schedule_date_roles
)

# =============================
# SHARED DATA FIXTURES
# =============================
# These fixtures provide standardized test data that can be reused across test files.
# Tests can use slicing/indexing to get subsets as needed (e.g., test_users_data[:2])

@pytest.fixture
def test_users_data():
    """Standard fixture providing array of test user data (4 users with various fields)"""
    return [
        {"user_id": USER_ID_1, "first_name": "Alice", "last_name": "Smith", "phone": "555-1111", "email": "alice@example.com"},
        {"user_id": USER_ID_2, "first_name": "Bob", "last_name": "Jones", "phone": "555-2222", "email": "bob@example.com"},
        {"user_id": USER_ID_3, "first_name": "Carol", "last_name": "Lee", "phone": "555-3333", "email": None},
        {"user_id": USER_ID_4, "first_name": "Another", "last_name": "User", "phone": "555-5555", "email": "another@example.com"},
    ]

@pytest.fixture
def test_teams_data():
    """Standard fixture providing array of test team data (4 teams)"""
    return [
        {"team_id": TEAM_ID_1, "team_name": "Team 1", "team_code": "team_1"},
        {"team_id": TEAM_ID_2, "team_name": "Team 2", "team_code": "team_2"},
        {"team_id": TEAM_ID_3, "team_name": "Team 3", "team_code": "team_3"},
        {"team_id": TEAM_ID_4, "team_name": "Another Team", "team_code": "new_team"},
    ]

@pytest.fixture
def test_media_roles_data():
    """Standard fixture providing array of test media_role data"""
    return [
        {"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "ProPresenter", "sort_order": 10, "media_role_code": "propresenter"},
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Sound", "sort_order": 20, "media_role_code": "sound"},
        {"media_role_id": MEDIA_ROLE_ID_3, "media_role_name": "Lighting", "sort_order": 30, "media_role_code": "lighting"},
        {"media_role_id": MEDIA_ROLE_ID_4, "media_role_name": "New Role", "sort_order": 4, "media_role_code": "new_role"},
        {"media_role_id": MEDIA_ROLE_ID_4, "media_role_name": "Another Role", "sort_order": 5, "media_role_code": "another_role"},
    ]

@pytest.fixture
def test_proficiency_levels_data():
    """Standard fixture providing array of test proficiency_level data"""
    return [
        {"proficiency_level_id": PROFICIENCY_LEVEL_ID_1, "proficiency_level_name": "Novice", "proficiency_level_number": 3, "proficiency_level_code": "novice", "is_assignable": True},
        {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2, "proficiency_level_name": "Proficient", "proficiency_level_number": 4, "proficiency_level_code": "proficient", "is_assignable": True},
        {"proficiency_level_id": PROFICIENCY_LEVEL_ID_3, "proficiency_level_name": "Untrained", "proficiency_level_number": 0, "proficiency_level_code": "untrained", "is_assignable": True},
        {"proficiency_level_id": PROFICIENCY_LEVEL_ID_4, "proficiency_level_name": "New Level", "proficiency_level_number": 5, "proficiency_level_code": "new_level"},
        {"proficiency_level_id": PROFICIENCY_LEVEL_ID_4, "proficiency_level_name": "Another Level", "proficiency_level_number": 5, "proficiency_level_code": "another_level"},
    ]

@pytest.fixture
def test_dates_data():
    """Standard fixture providing array of test date strings"""
    return [DATE_2024_02_29, DATE_2025_01_01, DATE_2025_03_31, DATE_2025_05_01, DATE_2025_05_02, DATE_2025_05_03, DATE_2025_08_31, DATE_2025_12_31]

@pytest.fixture
def test_schedule_date_types_data():
    """Standard fixture providing array of test schedule_date_type data"""
    return [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Rehearsal", "schedule_date_type_code": "rehearsal"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_4, "schedule_date_type_name": "New Type", "schedule_date_type_code": "new_type"},
    ]

@pytest.fixture
def test_team_users_data():
    """Standard fixture providing array of test team_user data"""
    return [
        {"team_id": TEAM_ID_1, "user_id": USER_ID_1},
        {"team_id": TEAM_ID_2, "user_id": USER_ID_1},
        {"team_id": TEAM_ID_1, "user_id": USER_ID_2},
        {"team_id": TEAM_ID_2, "user_id": USER_ID_3},
    ]

@pytest.fixture
def test_user_roles_data():
    """Standard fixture providing array of test user_role data"""
    return [
        {"user_id": USER_ID_1, "media_role_id": MEDIA_ROLE_ID_1, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1},
        {"user_id": USER_ID_1, "media_role_id": MEDIA_ROLE_ID_2, "proficiency_level_id": PROFICIENCY_LEVEL_ID_2},
        {"user_id": USER_ID_2, "media_role_id": MEDIA_ROLE_ID_1, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1},
        {"user_id": USER_ID_3, "media_role_id": MEDIA_ROLE_ID_2, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1},
    ]

@pytest.fixture
def test_user_dates_data():
    """Standard fixture providing array of test user_date data"""
    return [
        {"user_id": USER_ID_1, "date": DATE_2024_02_29},
        {"user_id": USER_ID_1, "date": DATE_2025_01_01},
        {"user_id": USER_ID_1, "date": DATE_2025_03_31},
        {"user_id": USER_ID_2, "date": DATE_2024_02_29},
        {"user_id": USER_ID_2, "date": DATE_2025_01_01},
        {"user_id": USER_ID_2, "date": DATE_2025_03_31},
    ]

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
