import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, SCHEDULE_DATE_TYPE_ID_1, SCHEDULE_DATE_TYPE_ID_2,
    SCHEDULE_DATE_TYPE_ID_3, SCHEDULE_DATE_TYPE_ID_4
)

# =============================
# GET ALL SCHEDULE DATE TYPES
# =============================
@pytest.mark.asyncio
async def test_get_all_schedule_date_types_none_exist(async_client):
    """Test when no schedule date types exist returns empty list"""
    response = await async_client.get("/schedule_date_types")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedule_date_types_success(async_client, seed_schedule_date_types, test_schedule_date_types_data):
    """Test getting all schedule date types after inserting a variety"""
    await seed_schedule_date_types(test_schedule_date_types_data[:2])

    response = await async_client.get("/schedule_date_types")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2
    assert response_json[0]["schedule_date_type_name"] == "Service"
    assert response_json[1]["schedule_date_type_id"] is not None
    assert response_json[1]["schedule_date_type_code"] == "rehearsal"
    assert response_json[1]["is_active"] is True

# =============================
# GET SINGLE SCHEDULE DATE TYPE
# =============================
@pytest.mark.parametrize("schedule_date_type_id, expected_status", [
    # Schedule date type not present
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_schedule_date_type_error_cases(async_client, schedule_date_type_id, expected_status):
    """Test GET single schedule date type error cases (404 and 422)"""
    response = await async_client.get(f"/schedule_date_types/{schedule_date_type_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_schedule_date_type_success(async_client, seed_schedule_date_types, test_schedule_date_types_data):
    """Test GET single schedule date type success case"""
    await seed_schedule_date_types(test_schedule_date_types_data[:2])
    
    response = await async_client.get(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["schedule_date_type_name"] == "Rehearsal"
    assert response_json["schedule_date_type_code"] == "rehearsal"
    assert response_json["is_active"] is True

# =============================
# INSERT SCHEDULE DATE TYPE
# =============================
@pytest.mark.parametrize("type_indices, payload, expected_status", [
    # empty payload
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields
    ([], {"schedule_date_type_name": "Incomplete Type"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid data types
    ([], {"schedule_date_type_name": "Bad Type", "schedule_date_type_code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # duplicate schedule_date_type_code
    ([2], {"schedule_date_type_name": "Duplicate Code", "schedule_date_type_code": "new_type"}, status.HTTP_409_CONFLICT),
    # schedule_date_type_id not allowed in payload
    ([], {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_4, "schedule_date_type_name": "Duplicate ID Type", "schedule_date_type_code": "duplicate_id_type"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_insert_schedule_date_type_error_cases(async_client, seed_schedule_date_types, test_schedule_date_types_data, type_indices, payload, expected_status):
    """Test INSERT schedule date type error cases (422 and 409)"""
    await conditional_seed(type_indices, test_schedule_date_types_data, seed_schedule_date_types)
    response = await async_client.post("/schedule_date_types", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_schedule_date_type_success(async_client):
    """Test valid schedule date type insertion"""
    response = await async_client.post("/schedule_date_types", json={
        "schedule_date_type_name": "New Type",
        "schedule_date_type_code": "new_type"
    })
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["schedule_date_type_id"] is not None
    assert response_json["schedule_date_type_name"] == "New Type"
    assert response_json["schedule_date_type_code"] == "new_type"
    assert response_json["is_active"] is True

# =============================
# UPDATE SCHEDULE DATE TYPE
# =============================
@pytest.mark.parametrize("schedule_date_type_path, payload, expected_status", [
    # schedule date type not found
    (f"/schedule_date_types/{BAD_ID_0000}", {"schedule_date_type_name": "Updated Type Name", "is_active": False}, status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ("/schedule_date_types/invalid-uuid-format", {"schedule_date_type_name": "Updated Type Name", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    (f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
    # invalid data types
    (f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_3}", {"schedule_date_type_name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # non-updatable field
    (f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_3}", {"schedule_date_type_name": "Invalid", "schedule_date_type_code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_update_schedule_date_type_error_cases(async_client, schedule_date_type_path, payload, expected_status):
    """Test UPDATE schedule date type error cases (400, 404, and 422)"""
    response = await async_client.patch(schedule_date_type_path, json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("schedule_date_type_id, payload, expected_fields, unchanged_fields", [
    # full update
    (
        SCHEDULE_DATE_TYPE_ID_2,
        {"schedule_date_type_name": "Updated Type Name", "is_active": False},
        {"schedule_date_type_name": "Updated Type Name", "is_active": False},
        {"schedule_date_type_code": "rehearsal"}
    ),
    # partial update (is_active only)
    (
        SCHEDULE_DATE_TYPE_ID_2,
        {"is_active": False},
        {"is_active": False},
        {"schedule_date_type_name": "Rehearsal", "schedule_date_type_code": "rehearsal"}
    ),
    # partial update (schedule_date_type_name only)
    (
        SCHEDULE_DATE_TYPE_ID_1,
        {"schedule_date_type_name": "Partially Updated Type"},
        {"schedule_date_type_name": "Partially Updated Type"},
        {"schedule_date_type_code": "service", "is_active": True}
    ),
])
@pytest.mark.asyncio
async def test_update_schedule_date_type_success(async_client, seed_schedule_date_types, test_schedule_date_types_data, schedule_date_type_id, payload, expected_fields, unchanged_fields):
    """Test valid schedule date type updates"""
    await seed_schedule_date_types(test_schedule_date_types_data[:2])
    
    response = await async_client.patch(f"/schedule_date_types/{schedule_date_type_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value
    for field, expected_value in unchanged_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE SCHEDULE DATE TYPE
# =============================
@pytest.mark.parametrize("schedule_date_type_path, expected_status", [
    # schedule date type not found
    (f"/schedule_date_types/{BAD_ID_0000}", status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ("/schedule_date_types/invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_schedule_date_type_error_cases(async_client, schedule_date_type_path, expected_status):
    """Test DELETE schedule date type error cases (404 and 422)"""
    response = await async_client.delete(schedule_date_type_path)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_schedule_date_type_success(async_client, seed_schedule_date_types, test_schedule_date_types_data):
    """Test successful schedule date type deletion with verification"""
    await seed_schedule_date_types([test_schedule_date_types_data[1]])

    response = await async_client.delete(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_2

    verify_response = await async_client.get(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_2}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND
