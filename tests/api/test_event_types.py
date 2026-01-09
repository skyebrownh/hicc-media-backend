import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, assert_single_item_201, conditional_seed
from tests.utils.constants import BAD_ID_0000, EVENT_TYPE_ID_1, EVENT_TYPE_ID_2, EVENT_TYPE_ID_3, EVENT_TYPE_ID_4

# =============================
# GET ALL EVENT TYPES
# =============================
@pytest.mark.asyncio
async def test_get_all_event_types_none_exist(async_client):
    """Test when no event types exist returns empty list"""
    response = await async_client.get("/event_types")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_event_types_success(async_client, seed_event_types, test_event_types_data):
    """Test getting all event types after inserting a variety"""
    seed_event_types(test_event_types_data[:2])
    response = await async_client.get("/event_types")
    assert_list_200(response, expected_length=2)
    response_json = response.json()
    assert response_json[0]["name"] == "Service"
    assert response_json[1]["id"] is not None
    assert response_json[1]["code"] == "rehearsal"
    assert response_json[1]["is_active"] is True

# =============================
# GET SINGLE EVENT TYPE
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Event type not present
    ("invalid-uuid-format", status.HTTP_400_BAD_REQUEST), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_event_type_error_cases(async_client, id, expected_status):
    """Test GET single event type error cases (400, 404)"""
    response = await async_client.get(f"/event_types/{id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_event_type_success(async_client, seed_event_types, test_event_types_data):
    """Test GET single event type success case"""
    seed_event_types([test_event_types_data[0]])
    response = await async_client.get(f"/event_types/{EVENT_TYPE_ID_1}")
    assert_single_item_200(response, expected_item={
        "id": EVENT_TYPE_ID_1,
        "name": "Service",
        "code": "service",
        "is_active": True
    })

# =============================
# INSERT EVENT TYPE
# =============================
@pytest.mark.parametrize("type_indices, payload, expected_status", [    
    ([], {}, status.HTTP_400_BAD_REQUEST), # empty payload
    ([], {"name": "Incomplete Type"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    ([], {"name": "Bad Type", "code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([2], {"name": "Duplicate Code", "code": "new_type"}, status.HTTP_409_CONFLICT), # duplicate event_type_code
    ([], {"id": EVENT_TYPE_ID_4, "name": "ID Not Allowed", "code": "id_not_allowed"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # event_type_id not allowed in payload
])
@pytest.mark.asyncio
async def test_insert_event_type_error_cases(async_client, seed_event_types, test_event_types_data, type_indices, payload, expected_status):
    """Test INSERT event type error cases (400, 422, and 409)"""
    conditional_seed(type_indices, test_event_types_data, seed_event_types)
    response = await async_client.post("/event_types", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_event_type_success(async_client):
    """Test valid event type insertion"""
    response = await async_client.post("/event_types", json={"name": "New Type", "code": "new_type"})
    assert_single_item_201(response, expected_item={"name": "New Type", "code": "new_type", "is_active": True})

# =============================
# UPDATE EVENT TYPE
# =============================
@pytest.mark.parametrize("event_type_indices, event_type_id, payload, expected_status", [
    ([], BAD_ID_0000, {"name": "Updated Event Type Name", "is_active": False}, status.HTTP_404_NOT_FOUND), # event type not found
    ([], "invalid-uuid-format", {"name": "Updated Event Type Name", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    ([0], EVENT_TYPE_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    ([0], EVENT_TYPE_ID_1, {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([0], EVENT_TYPE_ID_1, {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
@pytest.mark.asyncio
async def test_update_event_type_error_cases(async_client, seed_event_types, test_event_types_data, event_type_indices, event_type_id, payload, expected_status):
    """Test UPDATE event type error cases (400, 404, and 422)"""
    conditional_seed(event_type_indices, test_event_types_data, seed_event_types)
    response = await async_client.patch(f"/event_types/{event_type_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    ({"name": "Updated Event Type Name", "is_active": False}, {"code": "service"}), # full update
    ({"is_active": False}, {"name": "Service", "code": "service"}), # partial update (is_active only)
    ({"name": "Partially Updated Event Type"}, {"code": "service", "is_active": True}), # partial update (event_type_name only)
])
@pytest.mark.asyncio
async def test_update_event_type_success(async_client, seed_event_types, test_event_types_data, payload, unchanged_fields):
    """Test valid event type updates"""
    seed_event_types([test_event_types_data[0]])
    response = await async_client.patch(f"/event_types/{EVENT_TYPE_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == getattr(test_event_types_data[0], field)

# =============================
# DELETE EVENT TYPE
# =============================
@pytest.mark.asyncio
async def test_delete_event_type_error_cases(async_client):
    """Test DELETE event type error cases (400)"""
    response = await async_client.delete("/event_types/invalid-uuid-format")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_delete_event_type_success(async_client, seed_event_types, test_event_types_data):
    """Test successful event type deletion with verification"""
    seed_event_types([test_event_types_data[0]])
    response = await async_client.delete(f"/event_types/{EVENT_TYPE_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/event_types/{EVENT_TYPE_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify valid event type id that does not exist returns 204
    verify_response2 = await async_client.delete(f"/event_types/{BAD_ID_0000}")
    assert verify_response2.status_code == status.HTTP_204_NO_CONTENT
