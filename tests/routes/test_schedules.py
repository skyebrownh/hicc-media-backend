import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, SCHEDULE_ID_1, SCHEDULE_ID_2, SCHEDULE_ID_3, SCHEDULE_DATE_TYPE_ID_1,
    DATE_3, DATE_5, DATE_8, DATE_12, DATE_13, DATE_14, DATE_15
)

# =============================
# DATA FIXTURES
# =============================
@pytest.fixture
def test_dates_data():
    """Fixture providing array of test date strings"""
    return [DATE_5, DATE_3, DATE_12, DATE_8, DATE_13, DATE_14]

@pytest.fixture
def test_schedules_data():
    """Fixture providing array of test schedule data"""
    return [
        {"schedule_id": SCHEDULE_ID_1, "month_start_date": DATE_5, "notes": "First schedule"},
        {"schedule_id": SCHEDULE_ID_2, "month_start_date": DATE_3, "notes": "Second schedule"},
        {"schedule_id": SCHEDULE_ID_3, "month_start_date": DATE_12, "notes": None},
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
        {"schedule_id": SCHEDULE_ID_1, "date": DATE_8, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_id": SCHEDULE_ID_1, "date": DATE_13, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
        {"schedule_id": SCHEDULE_ID_1, "date": DATE_14, "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1},
    ]

# =============================
# GET ALL SCHEDULES
# =============================
@pytest.mark.asyncio
async def test_get_all_schedules_none_exist(async_client):
    """Test when no schedules exist returns empty list"""
    response = await async_client.get("/schedules")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedules_success(async_client, seed_dates, seed_schedules, test_schedules_data, test_dates_data):
    """Test getting all schedules after inserting a variety"""
    await seed_dates(test_dates_data[:3])
    await seed_schedules(test_schedules_data)

    response = await async_client.get("/schedules")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["month_start_date"] == DATE_5
    assert response_json[1]["schedule_id"] is not None
    assert response_json[1]["notes"] == "Second schedule"
    assert response_json[2]["is_active"] is True

# =============================
# GET ALL SCHEDULE DATES FOR SCHEDULE
# =============================
@pytest.mark.parametrize("schedule_id, expected_status", [
    # Schedule not present
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_all_schedule_dates_for_schedule_error_cases(async_client, schedule_id, expected_status):
    """Test GET all schedule dates for schedule error cases (404 and 422)"""
    response = await async_client.get(f"/schedules/{schedule_id}/schedule_dates")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_all_schedule_dates_for_schedule_none_exist(async_client, seed_dates, seed_schedules, seed_schedule_date_types, test_schedule_date_types_data, test_dates_data, test_schedules_data):
    """Test when no schedule dates exist returns empty list"""
    await seed_dates([test_dates_data[0], test_dates_data[3], test_dates_data[4], test_dates_data[5]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types(test_schedule_date_types_data)

    response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedule_dates_for_schedule_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_schedule_date_types_data, test_dates_data, test_schedules_data, test_schedule_dates_data):
    """Test getting all schedule dates for a schedule after inserting a variety"""
    await seed_dates([test_dates_data[0], test_dates_data[3], test_dates_data[4], test_dates_data[5]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_schedule_dates(test_schedule_dates_data)
    
    response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["date"] == DATE_8
    assert response_json[1]["date"] == DATE_13
    assert response_json[2]["date"] == DATE_14
    assert response_json[1]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response_json[1]["notes"] is None
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE SCHEDULE
# =============================
@pytest.mark.parametrize("schedule_id, expected_status", [
    # Schedule not present
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_schedule_error_cases(async_client, schedule_id, expected_status):
    """Test GET single schedule error cases (404 and 422)"""
    response = await async_client.get(f"/schedules/{schedule_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_schedule_success(async_client, seed_dates, seed_schedules, test_schedules_data, test_dates_data):
    """Test GET single schedule success case"""
    await seed_dates(test_dates_data[:3])
    await seed_schedules([test_schedules_data[0], test_schedules_data[1]])

    response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["month_start_date"] == DATE_3
    assert response_json["notes"] == "Second schedule"
    assert response_json["is_active"] is True

# =============================
# INSERT SCHEDULE
# =============================
@pytest.mark.parametrize("date_indices, payload, expected_status", [
    # empty payload
    ([3], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields
    ([3], {"notes": "missing required month_start_date"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid data types
    ([3], {"month_start_date": 12345, "notes": 999}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # schedule_id not allowed in payload
    ([3], {"schedule_id": "f8d3e340-9563-4de1-9146-675a8436242e", "month_start_date": DATE_8}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # foreign key constraint violation
    ([3], {"month_start_date": DATE_15}, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_insert_schedule_error_cases(async_client, seed_dates, test_dates_data, date_indices, payload, expected_status):
    """Test INSERT schedule error cases (422 and 404)"""
    await conditional_seed(date_indices, test_dates_data, seed_dates)
    
    response = await async_client.post("/schedules", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_schedule_success(async_client, seed_dates, test_dates_data):
    """Test valid schedule insertion"""
    await seed_dates([test_dates_data[3]])
    
    response = await async_client.post("/schedules", json={
        "month_start_date": DATE_8,
        "notes": "New schedule"
    })
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["schedule_id"] is not None
    assert response_json["month_start_date"] == DATE_8
    assert response_json["notes"] == "New schedule"
    assert response_json["is_active"] is True

# =============================
# UPDATE SCHEDULE
# =============================
@pytest.mark.parametrize("schedule_indices, schedule_path, payload, expected_status", [
    # schedule not found
    ([], f"/schedules/{BAD_ID_0000}", {"notes": "Updated schedule", "is_active": False}, status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ([0], "/schedules/invalid-uuid-format", {"notes": "Updated schedule", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    ([2], f"/schedules/{SCHEDULE_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
    # invalid data types
    ([2], f"/schedules/{SCHEDULE_ID_3}", {"month_start_date": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # non-updatable field
    ([2], f"/schedules/{SCHEDULE_ID_3}", {"schedule_id": SCHEDULE_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_update_schedule_error_cases(async_client, seed_dates, seed_schedules, test_schedules_data, schedule_indices, schedule_path, payload, expected_status):
    """Test UPDATE schedule error cases (400, 404, and 422)"""
    await conditional_seed(range(len(test_schedules_data)), [s["month_start_date"] for s in test_schedules_data], seed_dates)
    await conditional_seed(schedule_indices, test_schedules_data, seed_schedules)
    
    response = await async_client.patch(schedule_path, json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("schedule_id, payload, expected_fields, unchanged_fields", [
    # full update
    (
        SCHEDULE_ID_3,
        {"notes": "Updated schedule", "is_active": False},
        {"notes": "Updated schedule", "is_active": False},
        {"month_start_date": DATE_12}
    ),
    # partial update (is_active only)
    (
        SCHEDULE_ID_2,
        {"is_active": False},
        {"is_active": False},
        {"month_start_date": DATE_3}
    ),
    # partial update (notes only)
    (
        SCHEDULE_ID_1,
        {"notes": "Partially Updated"},
        {"notes": "Partially Updated"},
        {"month_start_date": DATE_5, "is_active": True}
    ),
])
@pytest.mark.asyncio
async def test_update_schedule_success(async_client, seed_dates, seed_schedules, test_schedules_data, test_dates_data, schedule_id, payload, expected_fields, unchanged_fields):
    """Test valid schedule updates"""
    await seed_dates(test_dates_data[:3])
    await seed_schedules(test_schedules_data)
    
    response = await async_client.patch(f"/schedules/{schedule_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value
    for field, expected_value in unchanged_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE SCHEDULE
# =============================
@pytest.mark.parametrize("schedule_indices, schedule_path, expected_status", [
    # schedule not found
    ([], f"/schedules/{BAD_ID_0000}", status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ([0], "/schedules/invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_schedule_error_cases(async_client, seed_dates, seed_schedules, test_schedules_data, schedule_indices, schedule_path, expected_status):
    """Test DELETE schedule error cases (404 and 422)"""
    if schedule_indices:
        schedules = [test_schedules_data[i] for i in schedule_indices]
        dates = [s["month_start_date"] for s in schedules]
        await seed_dates(dates)
        await seed_schedules(schedules)
    
    response = await async_client.delete(schedule_path)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_schedule_success(async_client, seed_dates, seed_schedules, test_schedules_data, test_dates_data):
    """Test successful schedule deletion"""
    await seed_dates(test_dates_data[:3])
    await seed_schedules([test_schedules_data[1]])

    response = await async_client.delete(f"/schedules/{SCHEDULE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["month_start_date"] == DATE_3
    assert response_json["schedule_id"] == SCHEDULE_ID_2

# =============================
# DELETE SCHEDULE DATES FOR SCHEDULE
# =============================
@pytest.mark.parametrize("schedule_id, expected_status", [
    # Schedule not present
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_schedule_dates_for_schedule_error_cases(async_client, schedule_id, expected_status):
    """Test DELETE schedule dates for schedule error cases (404 and 422)"""
    response = await async_client.delete(f"/schedules/{schedule_id}/schedule_dates")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_schedule_dates_for_schedule_none_exist(async_client, seed_dates, seed_schedules, seed_schedule_date_types, test_schedule_date_types_data, test_dates_data, test_schedules_data):
    """Test DELETE schedule dates for schedule when none exist returns empty list"""
    await seed_dates([test_dates_data[0], test_dates_data[3]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types(test_schedule_date_types_data)

    response = await async_client.delete(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 0
    assert response_json == []

@pytest.mark.asyncio
async def test_delete_schedule_dates_for_schedule_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_schedule_date_types_data, test_dates_data, test_schedules_data, test_schedule_dates_data):
    """Test successful deletion of all schedule dates for a schedule when schedule dates exist"""
    await seed_dates([test_dates_data[0], test_dates_data[3]])
    await seed_schedules([test_schedules_data[0]])
    await seed_schedule_date_types(test_schedule_date_types_data)
    await seed_schedule_dates([test_schedule_dates_data[0]])

    response = await async_client.delete(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1
    assert response_json[0]["date"] == DATE_8
    assert response_json[0]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert_empty_list_200(verify_response)
