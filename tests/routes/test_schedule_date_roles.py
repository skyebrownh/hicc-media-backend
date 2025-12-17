import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, SCHEDULE_ID_1, DATE_1, DATE_2, SCHEDULE_DATE_TYPE_ID_1,
    SCHEDULE_DATE_ID_1, SCHEDULE_DATE_ID_2, MEDIA_ROLE_ID_1, MEDIA_ROLE_ID_2, MEDIA_ROLE_ID_3,
    USER_ID_1, USER_ID_2, SCHEDULE_DATE_ROLE_ID_1, SCHEDULE_DATE_ROLE_ID_2, SCHEDULE_DATE_ROLE_ID_3
)

# =============================
# DATA FIXTURES
# =============================
@pytest.fixture
def test_dates_data():
    """Fixture providing array of test date strings"""
    return [DATE_1, DATE_2]

@pytest.fixture
def test_users_data():
    """Fixture providing array of test user data"""
    return [
        {"user_id": USER_ID_1, "first_name": "John", "last_name": "Doe", "phone": "555-0101"},
        {"user_id": USER_ID_2, "first_name": "Jane", "last_name": "Smith", "phone": "555-0102"},
    ]

@pytest.fixture
def test_schedules_data():
    """Fixture providing array of test schedule data"""
    return [
        {"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_1},
    ]

@pytest.fixture
def test_schedule_date_types_data():
    """Fixture providing array of test schedule_date_type data"""
    return [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Service", "schedule_date_type_code": "service"},
    ]

@pytest.fixture
def test_schedule_dates_data():
    """Fixture providing array of test schedule_date data"""
    return [
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "schedule_id": SCHEDULE_ID_1, "date": DATE_1, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "schedule_id": SCHEDULE_ID_1, "date": DATE_2, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
    ]

@pytest.fixture
def test_media_roles_data():
    """Fixture providing array of test media_role data"""
    return [
        {"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "ProPresenter", "sort_order": 10, "media_role_code": "propresenter"},
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Sound", "sort_order": 20, "media_role_code": "sound"},
        {"media_role_id": MEDIA_ROLE_ID_3, "media_role_name": "Lighting", "sort_order": 30, "media_role_code": "lighting"},
    ]

@pytest.fixture
def test_schedule_date_roles_data():
    """Fixture providing array of test schedule_date_role data"""
    return [
        {"schedule_date_role_id": SCHEDULE_DATE_ROLE_ID_1, "schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_1, "assigned_user_id": USER_ID_1},
        {"schedule_date_role_id": SCHEDULE_DATE_ROLE_ID_2, "schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2, "assigned_user_id": None},
        {"schedule_date_role_id": SCHEDULE_DATE_ROLE_ID_3, "schedule_date_id": SCHEDULE_DATE_ID_2, "media_role_id": MEDIA_ROLE_ID_1, "assigned_user_id": None},
    ]

# =============================
# GET ALL SCHEDULE DATE ROLES
# =============================
@pytest.mark.asyncio
async def test_get_all_schedule_date_roles_none_exist(async_client):
    """Test GET all schedule date roles when none exist"""
    response = await async_client.get("/schedule_date_roles")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedule_date_roles_success(async_client, seed_dates, seed_users, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_users_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data):
    """Test GET all schedule date roles success case"""
    await seed_dates(test_dates_data)
    await seed_users([test_users_data[0]])
    await seed_schedules(test_schedules_data)
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_schedule_dates(test_schedule_dates_data)
    await seed_media_roles(test_media_roles_data[:2])
    await seed_schedule_date_roles(test_schedule_date_roles_data)

    response = await async_client.get("/schedule_date_roles")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["schedule_date_role_id"] is not None
    assert response_json[0]["schedule_date_id"] == SCHEDULE_DATE_ID_1
    assert response_json[0]["media_role_id"] == MEDIA_ROLE_ID_1
    assert response_json[0]["assigned_user_id"] == USER_ID_1
    assert response_json[1]["is_active"] is True
    assert response_json[1]["is_required"] is True
    assert response_json[1]["is_preferred"] is False
    assert response_json[1]["assigned_user_id"] is None
    assert response_json[2]["schedule_date_id"] == SCHEDULE_DATE_ID_2
    assert response_json[2]["media_role_id"] == MEDIA_ROLE_ID_1

# =============================
# GET SINGLE SCHEDULE DATE ROLE
# =============================
@pytest.mark.parametrize("schedule_date_role_id, expected_status", [
    # Schedule date role not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_schedule_date_role_error_cases(async_client, schedule_date_role_id, expected_status):
    """Test GET single schedule date role error cases (404 and 422)"""
    response = await async_client.get(f"/schedule_date_roles/{schedule_date_role_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_schedule_date_role_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data):
    """Test GET single schedule date role success case"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules(test_schedules_data)
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_schedule_dates([test_schedule_dates_data[0]])
    await seed_media_roles([test_media_roles_data[1]])
    await seed_schedule_date_roles([test_schedule_date_roles_data[1]])
    
    response = await async_client.get(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["schedule_date_role_id"] == SCHEDULE_DATE_ROLE_ID_2
    assert response_json["schedule_date_id"] == SCHEDULE_DATE_ID_1
    assert response_json["media_role_id"] == MEDIA_ROLE_ID_2
    assert response_json["assigned_user_id"] is None
    assert response_json["is_required"] is True
    assert response_json["is_preferred"] is False
    assert response_json["is_active"] is True

# =============================
# INSERT SCHEDULE DATE ROLE
# =============================
@pytest.mark.parametrize("date_indices, schedule_indices, type_indices, schedule_date_indices, media_role_indices, schedule_date_role_indices, payload, expected_status", [
    # Empty payload
    ([], [], [], [], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Missing required fields (schedule_date_id)
    ([], [], [], [], [], [], {"media_role_id": MEDIA_ROLE_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Missing required fields (media_role_id)
    ([], [], [], [], [], [], {"schedule_date_id": SCHEDULE_DATE_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Invalid UUID format
    ([], [], [], [], [], [], {"schedule_date_id": "invalid-uuid", "media_role_id": MEDIA_ROLE_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Extra fields not allowed
    ([], [], [], [], [], [], {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2, "schedule_date_role_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Duplicate schedule_date_role
    ([0, 1], [0], [0], [0, 1], [0], [2], {"schedule_date_id": SCHEDULE_DATE_ID_2, "media_role_id": MEDIA_ROLE_ID_1}, status.HTTP_409_CONFLICT),
    # Foreign key violation (schedule_date doesn't exist)
    ([], [], [], [], [1], [], {"schedule_date_id": BAD_ID_0000, "media_role_id": MEDIA_ROLE_ID_2}, status.HTTP_404_NOT_FOUND),
    # Foreign key violation (media_role doesn't exist)
    ([0], [0], [0], [0], [], [], {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
    # Foreign key violation (user doesn't exist)
    ([0], [0], [0], [0], [1], [], {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2, "assigned_user_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_insert_schedule_date_role_error_cases(
    async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates,
    seed_media_roles, seed_schedule_date_roles, test_dates_data, test_schedules_data,
    test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data,
    date_indices, schedule_indices, type_indices, schedule_date_indices, media_role_indices,
    schedule_date_role_indices, payload, expected_status
):
    """Test INSERT schedule date role error cases (422, 409, and 404)"""
    await conditional_seed(date_indices, test_dates_data, seed_dates)
    await conditional_seed(schedule_indices, test_schedules_data, seed_schedules)
    await conditional_seed(type_indices, test_schedule_date_types_data, seed_schedule_date_types)
    await conditional_seed(schedule_date_indices, test_schedule_dates_data, seed_schedule_dates)
    await conditional_seed(media_role_indices, test_media_roles_data, seed_media_roles)
    await conditional_seed(schedule_date_role_indices, test_schedule_date_roles_data, seed_schedule_date_roles)
    
    response = await async_client.post("/schedule_date_roles", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, expected_fields", [
    # Basic insert
    (
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2},
        {"schedule_date_id": SCHEDULE_DATE_ID_1, "media_role_id": MEDIA_ROLE_ID_2, "is_required": False, "is_preferred": False, "is_active": True}
    ),
    # Insert with optional fields
    (
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "media_role_id": MEDIA_ROLE_ID_3, "assigned_user_id": USER_ID_2, "is_required": False, "is_preferred": True},
        {"schedule_date_id": SCHEDULE_DATE_ID_2, "media_role_id": MEDIA_ROLE_ID_3, "assigned_user_id": USER_ID_2, "is_required": False, "is_preferred": True}
    ),
])
@pytest.mark.asyncio
async def test_insert_schedule_date_role_success(async_client, seed_dates, seed_users, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, test_dates_data, test_users_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, payload, expected_fields):
    """Test INSERT schedule date role success cases"""
    await seed_dates(test_dates_data)
    await seed_users(test_users_data)
    await seed_schedules(test_schedules_data)
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_schedule_dates(test_schedule_dates_data)
    await seed_media_roles(test_media_roles_data)

    response = await async_client.post("/schedule_date_roles", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["schedule_date_role_id"] is not None
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value

# =============================
# UPDATE SCHEDULE DATE ROLE
# =============================
@pytest.mark.parametrize("schedule_date_role_id, payload, expected_status", [
    # Schedule date role not found
    (BAD_ID_0000, {"assigned_user_id": USER_ID_2}, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", {"assigned_user_id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Empty payload
    (SCHEDULE_DATE_ROLE_ID_1, {}, status.HTTP_400_BAD_REQUEST),
    # Foreign key violation (user doesn't exist)
    (SCHEDULE_DATE_ROLE_ID_1, {"assigned_user_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_update_schedule_date_role_error_cases(async_client, seed_users, test_users_data, schedule_date_role_id, payload, expected_status):
    """Test UPDATE schedule date role error cases (400, 404, and 422)"""
    await seed_users([test_users_data[1]])
    
    response = await async_client.patch(f"/schedule_date_roles/{schedule_date_role_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, expected_fields", [
    # Update assigned_user_id
    ({"assigned_user_id": USER_ID_2}, {"assigned_user_id": USER_ID_2}),
    # Update is_required
    ({"is_required": False}, {"is_required": False}),
    # Update is_preferred
    ({"is_preferred": True}, {"is_preferred": True}),
    # Update is_active
    ({"is_active": False}, {"is_active": False}),
])
@pytest.mark.asyncio
async def test_update_schedule_date_role_success(async_client, seed_dates, seed_users, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_users_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data, payload, expected_fields):
    """Test UPDATE schedule date role success cases"""
    await seed_dates([test_dates_data[0]])
    await seed_users(test_users_data)
    await seed_schedules(test_schedules_data)
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_schedule_dates([test_schedule_dates_data[0]])
    await seed_media_roles([test_media_roles_data[0]])
    await seed_schedule_date_roles([test_schedule_date_roles_data[0]])
    
    response = await async_client.patch(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE SCHEDULE DATE ROLE
# =============================
@pytest.mark.parametrize("schedule_date_role_id, expected_status", [
    # Schedule date role not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_schedule_date_role_error_cases(async_client, schedule_date_role_id, expected_status):
    """Test DELETE schedule date role error cases (404 and 422)"""
    response = await async_client.delete(f"/schedule_date_roles/{schedule_date_role_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_schedule_date_role_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data):
    """Test successful schedule date role deletion with verification"""
    await seed_dates([test_dates_data[0]])
    await seed_schedules(test_schedules_data)
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_schedule_dates([test_schedule_dates_data[0]])
    await seed_media_roles([test_media_roles_data[1]])
    await seed_schedule_date_roles([test_schedule_date_roles_data[1]])

    response = await async_client.delete(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["schedule_date_role_id"] == SCHEDULE_DATE_ROLE_ID_2

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_2}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND
