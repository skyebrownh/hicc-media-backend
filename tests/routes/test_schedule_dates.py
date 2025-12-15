import pytest
import pytest_asyncio
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, insert_dates, insert_schedules, insert_schedule_date_types, insert_schedule_dates, insert_teams, insert_media_roles, insert_schedule_date_roles, insert_users, insert_user_dates

# Test data constants
SCHEDULE_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
SCHEDULE_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
DATE_1 = "2025-01-15"
DATE_2 = "2025-01-20"
DATE_3 = "2025-02-01"
SCHEDULE_DATE_TYPE_ID_1 = "d0ececff-df86-404a-b2b6-8468b3b0aa33"
SCHEDULE_DATE_TYPE_ID_2 = "e1fdfd00-e097-415b-c3c7-9579c4c1bb44"
TEAM_ID_1 = "11a2b3c4-d5e6-4789-a012-b3c4d5e6f789"
SCHEDULE_DATE_ID_1 = "a1b2c3d4-e5f6-4789-a012-b3c4d5e6f789"
SCHEDULE_DATE_ID_2 = "b2c3d4e5-f6a7-4890-b123-c4d5e6f7a890"
SCHEDULE_DATE_ID_3 = "c3d4e5f6-a7b8-4901-c234-d5e6f7a8b901"
USER_ID_1 = "a1b2c3d4-e5f6-4789-a012-b3c4d5e6f789"
USER_ID_2 = "b2c3d4e5-f6a7-4890-b123-c4d5e6f7a890"
MEDIA_ROLE_ID_1 = "11a2b3c4-d5e6-4789-a012-b3c4d5e6f789"
MEDIA_ROLE_ID_2 = "22b3c4d5-e6f7-4890-b123-c4d5e6f7a890"

@pytest_asyncio.fixture
async def seed_schedules_helper(test_db_pool):
    """Helper fixture to seed schedules in the database"""
    async def seed_schedules(schedules: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_schedules(schedules))
    return seed_schedules

@pytest_asyncio.fixture
async def seed_schedule_date_types_helper(test_db_pool):
    """Helper fixture to seed schedule_date_types in the database"""
    async def seed_schedule_date_types(schedule_date_types: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_schedule_date_types(schedule_date_types))
    return seed_schedule_date_types

@pytest_asyncio.fixture
async def seed_schedule_dates_helper(test_db_pool):
    """Helper fixture to seed schedule_dates in the database"""
    async def seed_schedule_dates(schedule_dates: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_schedule_dates(schedule_dates))
    return seed_schedule_dates

@pytest_asyncio.fixture
async def seed_teams_helper(test_db_pool):
    """Helper fixture to seed teams in the database"""
    async def seed_teams(teams: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_teams(teams))
    return seed_teams

@pytest_asyncio.fixture
async def seed_media_roles_helper(test_db_pool):
    """Helper fixture to seed media roles in the database"""
    async def seed_media_roles(media_roles: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_media_roles(media_roles))
    return seed_media_roles

@pytest_asyncio.fixture
async def seed_schedule_date_roles_helper(test_db_pool):
    """Helper fixture to seed schedule_date_roles in the database"""
    async def seed_schedule_date_roles(schedule_date_roles: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_schedule_date_roles(schedule_date_roles))
    return seed_schedule_date_roles

@pytest_asyncio.fixture
async def seed_users_helper(test_db_pool):
    """Helper fixture to seed users in the database"""
    async def seed_users(users: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_users(users))
    return seed_users

@pytest_asyncio.fixture
async def seed_user_dates_helper(test_db_pool):
    """Helper fixture to seed user_dates in the database"""
    async def seed_user_dates(user_dates: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_user_dates(user_dates))
    return seed_user_dates

@pytest.mark.asyncio
async def test_get_all_schedule_dates(async_client, test_db_pool, seed_schedules_helper, seed_schedule_date_types_helper, seed_schedule_dates_helper):
    # 1. Test when no schedule dates exist
    response1 = await async_client.get("/schedule_dates")
    assert_empty_list_200(response1)

    # Seed schedules, dates, schedule_date_types, and schedule_dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2, DATE_3]))
    
    schedules = [
        {"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1},
        {"schedule_id": SCHEDULE_ID_2, "month_start_date": DATE_2},
    ]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Rehearsal", "schedule_date_type_code": "rehearsal"},
    ]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    schedule_dates = [
        {"schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_id": SCHEDULE_ID_2, "date": DATE_3, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2},
    ]
    await seed_schedule_dates_helper(schedule_dates)

    # 2. Test when schedule dates exist
    response2 = await async_client.get("/schedule_dates")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["schedule_date_id"] is not None
    assert response2_json[0]["schedule_id"] == SCHEDULE_ID_1
    assert response2_json[0]["date"] == DATE_1
    assert response2_json[1]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response2_json[1]["team_id"] is None
    assert response2_json[2]["notes"] is None
    assert response2_json[2]["is_active"] is True

@pytest.mark.asyncio
async def test_get_single_schedule_date(async_client, test_db_pool, seed_schedules_helper, seed_schedule_date_types_helper, seed_schedule_dates_helper):
    # Seed schedules, dates, schedule_date_types, and schedule_dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
    
    schedules = [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [{"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"}]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    schedule_dates = [{"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}]
    await seed_schedule_dates_helper(schedule_dates)

    # 1. Test when schedule date exists
    response1 = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, dict)
    assert response1_json["schedule_date_id"] == SCHEDULE_DATE_ID_1
    assert response1_json["schedule_id"] == SCHEDULE_ID_1
    assert response1_json["date"] == DATE_1
    assert response1_json["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response1_json["team_id"] is None
    assert response1_json["notes"] is None
    assert response1_json["is_active"] is True

    # 2. Test schedule date not found
    response2 = await async_client.get("/schedule_dates/00000000-0000-0000-0000-000000000000")
    assert response2.status_code == status.HTTP_404_NOT_FOUND

    # 3. Test invalid UUID format
    response3 = await async_client.get("/schedule_dates/invalid-uuid-format")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_get_all_schedule_date_roles_by_schedule_date(async_client, test_db_pool, seed_schedules_helper, seed_schedule_date_types_helper, seed_schedule_dates_helper, seed_media_roles_helper, seed_schedule_date_roles_helper):
    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
    
    schedules = [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [{"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"}]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    schedule_dates = [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
    ]
    await seed_schedule_dates_helper(schedule_dates)
    
    media_roles = [
        {"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "ProPresenter", "sort_order": 10, "media_role_code": "propresenter"},
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Sound", "sort_order": 20, "media_role_code": "sound"},
    ]
    await seed_media_roles_helper(media_roles)
    
    schedule_date_roles = [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2},
    ]
    await seed_schedule_date_roles_helper(schedule_date_roles)

    # 1. Test when schedule date has roles
    response1 = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert all(role["schedule_date_id"] == SCHEDULE_DATE_ID_1 for role in response1_json)

    # 2. Test when schedule date has no roles
    response2 = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_2}/roles")
    assert_empty_list_200(response2)

    # 3. Test invalid UUID format
    response3 = await async_client.get("/schedule_dates/invalid-uuid-format/roles")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test schedule date not found
    response4 = await async_client.get("/schedule_dates/00000000-0000-0000-0000-000000000000/roles")
    assert response4.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_user_dates_by_schedule_date(async_client, test_db_pool, seed_users_helper, seed_schedules_helper, seed_schedule_date_types_helper, seed_schedule_dates_helper, seed_user_dates_helper):
    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
    
    users = [
        {"user_id": USER_ID_1, "first_name": "John", "last_name": "Doe", "phone": "555-0101"},
        {"user_id": USER_ID_2, "first_name": "Jane", "last_name": "Smith", "phone": "555-0102"},
    ]
    await seed_users_helper(users)
    
    schedules = [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [{"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"}]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    schedule_dates = [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
    ]
    await seed_schedule_dates_helper(schedule_dates)
    
    user_dates = [
        {"user_id": USER_ID_1, "date": DATE_1},
        {"user_id": USER_ID_2, "date": DATE_1},
    ]
    await seed_user_dates_helper(user_dates)

    # 1. Test when schedule date has user dates
    response1 = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/user_dates")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert response1_json[0]["date"] == DATE_1
    assert response1_json[1]["date"] == DATE_1

    # 2. Test when schedule date has no user dates
    response2 = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_2}/user_dates")
    assert_empty_list_200(response2)

    # 3. Test invalid UUID format
    response3 = await async_client.get("/schedule_dates/invalid-uuid-format/user_dates")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test schedule date not found
    response4 = await async_client.get("/schedule_dates/00000000-0000-0000-0000-000000000000/user_dates")
    assert response4.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_insert_schedule_date(async_client, test_db_pool, seed_schedules_helper, seed_schedule_date_types_helper, seed_teams_helper, seed_schedule_dates_helper):
    # Seed schedules, dates, and schedule_date_types data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
    
    schedules = [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Rehearsal", "schedule_date_type_code": "rehearsal"},
    ]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    teams = [{"team_id": TEAM_ID_1, "team_name": "Team 1", "team_code": "team_1"}]
    await seed_teams_helper(teams)
    
    schedule_dates = [{"schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}]
    await seed_schedule_dates_helper(schedule_dates)

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"schedule_id": SCHEDULE_ID_1}  # Missing date and schedule_date_type_id
    bad_payload_3 = {"date": DATE_2}  # Missing schedule_id and schedule_date_type_id
    bad_payload_4 = {"schedule_id": "invalid-uuid", "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}  # Invalid UUID
    good_payload = {
        "schedule_id": SCHEDULE_ID_1,
        "date": DATE_2,
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1
    }
    bad_payload_5 = {
        "schedule_id": SCHEDULE_ID_1,
        "date": DATE_1,
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1  # Duplicate (already exists)
    }
    bad_payload_6 = {
        "schedule_id": SCHEDULE_ID_1,
        "date": DATE_2,
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1,
        "schedule_date_id": "00000000-0000-0000-0000-000000000000"  # schedule_date_id not allowed
    }
    bad_payload_7 = {
        "schedule_id": "00000000-0000-0000-0000-000000000000",
        "date": DATE_2,
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1  # Foreign key violation (schedule doesn't exist)
    }
    bad_payload_8 = {
        "schedule_id": SCHEDULE_ID_1,
        "date": "2025-12-31",
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1  # Foreign key violation (date doesn't exist)
    }
    bad_payload_9 = {
        "schedule_id": SCHEDULE_ID_1,
        "date": DATE_2,
        "schedule_date_type_id": "00000000-0000-0000-0000-000000000000"  # Foreign key violation (schedule_date_type doesn't exist)
    }
    good_payload_with_optional = {
        "schedule_id": SCHEDULE_ID_1,
        "date": DATE_2,
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2,
        "team_id": TEAM_ID_1,
        "notes": "Test notes"
    }

    # 1. Test empty payload
    response1 = await async_client.post("/schedule_dates", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/schedule_dates", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test missing required fields
    response3 = await async_client.post("/schedule_dates", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid UUID format
    response4 = await async_client.post("/schedule_dates", json=bad_payload_4)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test valid payload
    response5 = await async_client.post("/schedule_dates", json=good_payload)
    assert response5.status_code == status.HTTP_201_CREATED
    response5_json = response5.json()
    assert response5_json["schedule_date_id"] is not None
    assert response5_json["schedule_id"] == SCHEDULE_ID_1
    assert response5_json["date"] == DATE_2
    assert response5_json["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response5_json["is_active"] is True

    # 6. Test duplicate schedule_date (same schedule_id + date + schedule_date_type_id combination)
    response6 = await async_client.post("/schedule_dates", json=bad_payload_5)
    assert response6.status_code == status.HTTP_409_CONFLICT

    # 7. Test extra fields not allowed in payload
    response7 = await async_client.post("/schedule_dates", json=bad_payload_6)
    assert response7.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 8. Test foreign key violation (schedule doesn't exist)
    response8 = await async_client.post("/schedule_dates", json=bad_payload_7)
    assert response8.status_code == status.HTTP_404_NOT_FOUND

    # 9. Test foreign key violation (date doesn't exist)
    response9 = await async_client.post("/schedule_dates", json=bad_payload_8)
    assert response9.status_code == status.HTTP_404_NOT_FOUND

    # 10. Test foreign key violation (schedule_date_type doesn't exist)
    response10 = await async_client.post("/schedule_dates", json=bad_payload_9)
    assert response10.status_code == status.HTTP_404_NOT_FOUND

    # 11. Test valid payload with optional fields
    response11 = await async_client.post("/schedule_dates", json=good_payload_with_optional)
    assert response11.status_code == status.HTTP_201_CREATED
    response11_json = response11.json()
    assert response11_json["team_id"] == TEAM_ID_1
    assert response11_json["notes"] == "Test notes"

@pytest.mark.asyncio
async def test_update_schedule_date(async_client, test_db_pool, seed_schedules_helper, seed_schedule_date_types_helper, seed_teams_helper, seed_schedule_dates_helper):
    # Seed schedules, dates, schedule_date_types, and schedule_dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2, DATE_3]))
    
    schedules = [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Rehearsal", "schedule_date_type_code": "rehearsal"},
    ]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    teams = [{"team_id": TEAM_ID_1, "team_name": "Team 1", "team_code": "team_1"}]
    await seed_teams_helper(teams)
    
    schedule_dates = [{"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}]
    await seed_schedule_dates_helper(schedule_dates)

    # Set up payloads
    bad_payload_1 = {}
    good_payload_1 = {
        "notes": "Updated notes"
    }
    good_payload_2 = {
        "team_id": TEAM_ID_1
    }
    good_payload_3 = {
        "is_active": False
    }
    good_payload_4 = {
        "date": DATE_2,
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2
    }

    # 1. Test schedule date not found
    response1 = await async_client.patch("/schedule_dates/00000000-0000-0000-0000-000000000000", json=good_payload_1)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/schedule_dates/invalid-uuid-format", json=good_payload_1)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/schedule_dates/{SCHEDULE_DATE_ID_1}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test valid payload (update notes)
    response4 = await async_client.patch(f"/schedule_dates/{SCHEDULE_DATE_ID_1}", json=good_payload_1)
    assert response4.status_code == status.HTTP_200_OK
    response4_json = response4.json()
    assert response4_json["notes"] == "Updated notes"

    # 5. Test valid payload (update team_id)
    response5 = await async_client.patch(f"/schedule_dates/{SCHEDULE_DATE_ID_1}", json=good_payload_2)
    assert response5.status_code == status.HTTP_200_OK
    response5_json = response5.json()
    assert response5_json["team_id"] == TEAM_ID_1

    # 6. Test valid payload (update is_active)
    response6 = await async_client.patch(f"/schedule_dates/{SCHEDULE_DATE_ID_1}", json=good_payload_3)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["is_active"] is False

    # 7. Test valid payload (update date and schedule_date_type_id)
    response7 = await async_client.patch(f"/schedule_dates/{SCHEDULE_DATE_ID_1}", json=good_payload_4)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["date"] == DATE_2
    assert response7_json["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_2

@pytest.mark.asyncio
async def test_delete_schedule_date(async_client, test_db_pool, seed_schedules_helper, seed_schedule_date_types_helper, seed_schedule_dates_helper):
    # Seed schedules, dates, schedule_date_types, and schedule_dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
    
    schedules = [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [{"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"}]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    schedule_dates = [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
    ]
    await seed_schedule_dates_helper(schedule_dates)

    # 1. Test schedule date not found
    response1 = await async_client.delete("/schedule_dates/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/schedule_dates/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when schedule date exists
    response3 = await async_client.delete(f"/schedule_dates/{SCHEDULE_DATE_ID_1}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["schedule_date_id"] == SCHEDULE_DATE_ID_1

    # 4. Verify deletion by trying to get it again
    response4 = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}")
    assert response4.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_schedule_date_roles_for_schedule_date(async_client, test_db_pool, seed_schedules_helper, seed_schedule_date_types_helper, seed_schedule_dates_helper, seed_media_roles_helper, seed_schedule_date_roles_helper):
    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
    
    schedules = [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]
    await seed_schedules_helper(schedules)
    
    schedule_date_types = [{"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"}]
    await seed_schedule_date_types_helper(schedule_date_types)
    
    schedule_dates = [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
    ]
    await seed_schedule_dates_helper(schedule_dates)
    
    media_roles = [
        {"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "ProPresenter", "sort_order": 10, "media_role_code": "propresenter"},
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Sound", "sort_order": 20, "media_role_code": "sound"},
    ]
    await seed_media_roles_helper(media_roles)
    
    schedule_date_roles = [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2},
    ]
    await seed_schedule_date_roles_helper(schedule_date_roles)

    # 1. Test when schedule date has roles
    response1 = await async_client.delete(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert all(role["schedule_date_id"] == SCHEDULE_DATE_ID_1 for role in response1_json)

    # 2. Verify deletion by checking roles again
    response2 = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert response2.status_code == status.HTTP_200_OK
    assert len(response2.json()) == 0

    # 3. Test invalid UUID format
    response3 = await async_client.delete("/schedule_dates/invalid-uuid-format/roles")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test schedule date not found
    response4 = await async_client.delete("/schedule_dates/00000000-0000-0000-0000-000000000000/roles")
    assert response4.status_code == status.HTTP_404_NOT_FOUND
