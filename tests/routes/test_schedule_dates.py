import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, SCHEDULE_ID_1, SCHEDULE_DATE_TYPE_ID_1, SCHEDULE_DATE_TYPE_ID_2,
    SCHEDULE_DATE_ID_1, SCHEDULE_DATE_ID_2, SCHEDULE_DATE_ID_3, TEAM_ID_1, USER_ID_1, USER_ID_2,
    MEDIA_ROLE_ID_1, MEDIA_ROLE_ID_2, DATE_1, DATE_2, DATE_6
)

# =============================
# DATA FIXTURES
# =============================
@pytest.fixture
def test_dates_data():
    """Fixture providing array of test date strings"""
    return [DATE_1, DATE_2, DATE_6]

@pytest.fixture
def test_schedules_data():
    """Fixture providing array of test schedule data"""
    return [{"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1}]

@pytest.fixture
def test_schedule_date_types_data():
    """Fixture providing array of test schedule_date_type data"""
    return [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Rehearsal", "schedule_date_type_code": "rehearsal"},
    ]

@pytest.fixture
def test_teams_data():
    """Fixture providing array of test team data"""
    return [{"team_id": TEAM_ID_1, "team_name": "Team 1", "team_code": "team_1"}]

@pytest.fixture
def test_schedule_dates_data():
    """Fixture providing array of test schedule_date data"""
    return [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_3, "schedule_id": SCHEDULE_ID_1, "date": DATE_6, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}
    ]

@pytest.fixture
def test_users_data():
    """Fixture providing array of test user data"""
    return [
        {"user_id": USER_ID_1, "first_name": "John", "last_name": "Doe", "phone": "555-0101"},
        {"user_id": USER_ID_2, "first_name": "Jane", "last_name": "Smith", "phone": "555-0102"},
    ]

@pytest.fixture
def test_user_dates_data():
    """Fixture providing array of test user_date data"""
    return [
        {"user_id": USER_ID_1, "date": DATE_1},
        {"user_id": USER_ID_2, "date": DATE_1},
    ]

@pytest.fixture
def test_media_roles_data():
    """Fixture providing array of test media_role data"""
    return [
        {"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "ProPresenter", "sort_order": 10, "media_role_code": "propresenter"},
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Sound", "sort_order": 20, "media_role_code": "sound"},
    ]

@pytest.fixture
def test_schedule_date_roles_data():
    """Fixture providing array of test schedule_date_role data"""
    return [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2},
    ]

# =============================
# GET ALL SCHEDULE DATES
# =============================
@pytest.mark.asyncio
async def test_get_all_schedule_dates_none_exist(async_client):
    """Test when no schedule dates exist returns empty list"""
    response = await async_client.get("/schedule_dates")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedule_dates_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data):
    """Test getting all schedule dates after inserting a variety"""
    await seed_dates(test_dates_data)
    await seed_schedules(test_schedules_data)
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates(test_schedule_dates_data)

    response = await async_client.get("/schedule_dates")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["schedule_date_id"] is not None
    assert response_json[0]["schedule_id"] == SCHEDULE_ID_1
    assert response_json[0]["date"] == DATE_1
    assert response_json[1]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response_json[1]["team_id"] is None
    assert response_json[2]["notes"] is None
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE SCHEDULE DATE
# =============================
@pytest.mark.parametrize("schedule_date_id, expected_status", [
    # Schedule date not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_schedule_date_error_cases(async_client, schedule_date_id, expected_status):
    """Test GET single schedule date error cases (404 and 422)"""
    response = await async_client.get(f"/schedule_dates/{schedule_date_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_schedule_date_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data):
    """Test GET single schedule date success case"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])

    response = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["schedule_date_id"] == SCHEDULE_DATE_ID_1
    assert response_json["schedule_id"] == SCHEDULE_ID_1
    assert response_json["date"] == DATE_1
    assert response_json["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response_json["team_id"] is None
    assert response_json["notes"] is None
    assert response_json["is_active"] is True

# =============================
# GET ALL SCHEDULE DATE ROLES BY SCHEDULE DATE
# =============================
@pytest.mark.parametrize("schedule_date_id, expected_status", [
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Schedule date not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_get_all_schedule_date_roles_by_schedule_date_error_cases(async_client, schedule_date_id, expected_status):
    """Test GET all schedule date roles for schedule date error cases (404 and 422)"""
    response = await async_client.get(f"/schedule_dates/{schedule_date_id}/roles")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_all_schedule_date_roles_by_schedule_date_none_exist(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data):
    """Test GET all schedule date roles for schedule date when none exist returns empty list"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])

    response = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedule_date_roles_by_schedule_date_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data):
    """Test GET all schedule date roles for schedule date success case"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])
    await seed_media_roles(test_media_roles_data)
    await seed_schedule_date_roles(test_schedule_date_roles_data)

    response = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2
    assert all(role["schedule_date_id"] == SCHEDULE_DATE_ID_1 for role in response_json)

# =============================
# GET ALL USER DATES BY SCHEDULE DATE
# =============================
@pytest.mark.parametrize("schedule_date_id, expected_status", [
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Schedule date not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_get_all_user_dates_by_schedule_date_error_cases(async_client, schedule_date_id, expected_status):
    """Test GET all user dates for schedule date error cases (404 and 422)"""
    response = await async_client.get(f"/schedule_dates/{schedule_date_id}/user_dates")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_all_user_dates_by_schedule_date_none_exist(async_client, seed_dates, seed_users, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_dates_data, test_users_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data):
    """Test GET all user dates for schedule date when none exist returns empty list"""
    await seed_dates([test_dates_data[0]])
    await seed_users(test_users_data)
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])

    response = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/user_dates")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_user_dates_by_schedule_date_success(async_client, seed_dates, seed_users, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_user_dates, test_dates_data, test_users_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_user_dates_data):
    """Test GET all user dates for schedule date success case"""
    await seed_dates([test_dates_data[0], test_dates_data[1]])
    await seed_users(test_users_data)
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])
    await seed_user_dates(test_user_dates_data)

    response = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/user_dates")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2
    assert response_json[0]["date"] == DATE_1
    assert response_json[0]["user_id"] == USER_ID_1
    assert response_json[1]["date"] == DATE_1
    assert response_json[1]["user_id"] == USER_ID_2

# =============================
# INSERT SCHEDULE DATE
# =============================
@pytest.mark.parametrize("date_indices, schedule_indices, type_indices, schedule_date_indices, payload, expected_status", [
    # empty payload
    ([], [], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields (date and schedule_date_type_id)
    ([], [], [], [], {"schedule_id": SCHEDULE_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields (schedule_id and schedule_date_type_id)
    ([], [], [], [], {"date": DATE_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid UUID format
    ([], [], [], [], {"schedule_id": "invalid-uuid", "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # duplicate schedule_date
    ([0], [0], [0], [0], {"schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}, status.HTTP_409_CONFLICT),
    # extra fields not allowed
    ([], [], [], [], {"schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # foreign key violation (schedule doesn't exist)
    ([0, 1], [], [0], [], {"schedule_id": BAD_ID_0000, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}, status.HTTP_404_NOT_FOUND),
    # foreign key violation (date doesn't exist)
    ([0, 1], [0], [0], [], {"schedule_id": SCHEDULE_ID_1, "date": "2025-12-31", "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1}, status.HTTP_404_NOT_FOUND),
    # foreign key violation (schedule_date_type doesn't exist)
    ([0, 1], [0], [], [], {"schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_insert_schedule_date_error_cases(
    async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates,
    test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data,
    date_indices, schedule_indices, type_indices, schedule_date_indices, payload, expected_status
):
    """Test INSERT schedule date error cases (422, 409, and 404)"""
    await conditional_seed(date_indices, test_dates_data, seed_dates)
    await conditional_seed(schedule_indices, test_schedules_data, seed_schedules)
    await conditional_seed(type_indices, test_schedule_date_types_data, seed_schedule_date_types)
    await conditional_seed(schedule_date_indices, test_schedule_dates_data, seed_schedule_dates)
    response = await async_client.post("/schedule_dates", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_schedule_date_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, test_dates_data, test_schedules_data, test_schedule_date_types_data):
    """Test valid schedule date insertion"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    
    response = await async_client.post("/schedule_dates", json={
        "schedule_id": SCHEDULE_ID_1,
        "date": DATE_1,
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1
    })
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["schedule_date_id"] is not None
    assert response_json["schedule_id"] == SCHEDULE_ID_1
    assert response_json["date"] == DATE_1
    assert response_json["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response_json["is_active"] is True

# =============================
# UPDATE SCHEDULE DATE
# =============================
@pytest.mark.parametrize("schedule_date_id, payload, expected_status", [
    # schedule date not found
    (BAD_ID_0000, {"notes": "Updated notes"}, status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ("invalid-uuid-format", {"notes": "Updated notes"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    (SCHEDULE_DATE_ID_1, {}, status.HTTP_400_BAD_REQUEST),
])
@pytest.mark.asyncio
async def test_update_schedule_date_error_cases(async_client, schedule_date_id, payload, expected_status):
    """Test UPDATE schedule date error cases (400, 404, and 422)"""
    response = await async_client.patch(f"/schedule_dates/{schedule_date_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, expected_fields", [
    # update notes
    ({"notes": "Updated notes"}, {"notes": "Updated notes"}),
    # update team_id
    ({"team_id": TEAM_ID_1}, {"team_id": TEAM_ID_1}),
    # update is_active
    ({"is_active": False}, {"is_active": False}),
    # update date and schedule_date_type_id
    (
        {"date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2},
        {"date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2}
    ),
])
@pytest.mark.asyncio
async def test_update_schedule_date_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_teams, seed_schedule_dates, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_teams_data, test_schedule_dates_data, payload, expected_fields):
    """Test valid schedule date updates"""
    await seed_dates(test_dates_data)
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_teams(test_teams_data)
    await seed_schedule_dates([test_schedule_dates_data[0]])
    
    response = await async_client.patch(f"/schedule_dates/{SCHEDULE_DATE_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE SCHEDULE DATE
# =============================
@pytest.mark.parametrize("schedule_date_id, expected_status", [
    # schedule date not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_schedule_date_error_cases(async_client, schedule_date_id, expected_status):
    """Test DELETE schedule date error cases (404 and 422)"""
    response = await async_client.delete(f"/schedule_dates/{schedule_date_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_schedule_date_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data):
    """Test successful schedule date deletion with verification"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])

    response = await async_client.delete(f"/schedule_dates/{SCHEDULE_DATE_ID_1}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["schedule_date_id"] == SCHEDULE_DATE_ID_1

    verify_response = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

# =============================
# DELETE SCHEDULE DATE ROLES FOR SCHEDULE DATE
# =============================
@pytest.mark.parametrize("schedule_date_id, expected_status", [
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Schedule date not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_delete_schedule_date_roles_for_schedule_date_error_cases(async_client, schedule_date_id, expected_status):
    """Test DELETE schedule date roles for schedule date error cases (404 and 422)"""
    response = await async_client.delete(f"/schedule_dates/{schedule_date_id}/roles")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_schedule_date_roles_for_schedule_date_none_exist(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data):
    """Test DELETE schedule date roles for schedule date when none exist returns empty list"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])

    response = await async_client.delete(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 0

@pytest.mark.asyncio
async def test_delete_schedule_date_roles_for_schedule_date_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data):
    """Test successful deletion of all schedule date roles for a schedule date"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types([test_schedule_date_types_data[0]])
    await seed_schedule_dates([test_schedule_dates_data[0]])
    await seed_media_roles(test_media_roles_data)
    await seed_schedule_date_roles(test_schedule_date_roles_data)

    response = await async_client.delete(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2
    assert all(role["schedule_date_id"] == SCHEDULE_DATE_ID_1 for role in response_json)

    verify_response = await async_client.get(f"/schedule_dates/{SCHEDULE_DATE_ID_1}/roles")
    assert verify_response.status_code == status.HTTP_200_OK
    assert len(verify_response.json()) == 0
