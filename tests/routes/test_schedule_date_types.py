import pytest
import pytest_asyncio
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, insert_schedule_date_types

SCHEDULE_DATE_TYPE_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
SCHEDULE_DATE_TYPE_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
SCHEDULE_DATE_TYPE_ID_3 = "c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1"
SCHEDULE_DATE_TYPE_ID_4 = "e1fdfd00-e097-415b-c3c7-9579c4c1bb44"

@pytest_asyncio.fixture
async def seed_schedule_date_types_helper(test_db_pool):
    """Helper fixture to seed schedule_date_types in the database"""
    async def seed_schedule_date_types(schedule_date_types: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_schedule_date_types(schedule_date_types))
    return seed_schedule_date_types

@pytest.mark.asyncio
async def test_get_all_schedule_date_types(async_client, seed_schedule_date_types_helper):
    # 1. Test when no schedule date types exist
    response1 = await async_client.get("/schedule_date_types")
    assert_empty_list_200(response1)

    # Seed schedule date types data directly into test DB
    schedule_date_types = [
        {"schedule_date_type_name": "Type 1", "schedule_date_type_code": "type_1"},
        {"schedule_date_type_name": "Type 2", "schedule_date_type_code": "type_2"},
        {"schedule_date_type_name": "Type 3", "schedule_date_type_code": "type_3"},
    ]
    await seed_schedule_date_types_helper(schedule_date_types)

    # 2. Test when schedule date types exist
    response2 = await async_client.get("/schedule_date_types")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["schedule_date_type_name"] == "Type 1"
    assert response2_json[1]["schedule_date_type_id"] is not None
    assert response2_json[1]["schedule_date_type_code"] == "type_2"
    assert response2_json[2]["is_active"] is True

@pytest.mark.asyncio
async def test_get_single_schedule_date_type(async_client, seed_schedule_date_types_helper):
    # 1. Test when no schedule date types exist
    response1 = await async_client.get(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_1}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed schedule date types data directly into test DB
    schedule_date_types = [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Type 1", "schedule_date_type_code": "type_1"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Type 2", "schedule_date_type_code": "type_2"},
    ]
    await seed_schedule_date_types_helper(schedule_date_types)

    # 2. Test when schedule date types exist
    response2 = await async_client.get(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_2}")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, dict)
    assert response2_json["schedule_date_type_name"] == "Type 2"
    assert response2_json["schedule_date_type_code"] == "type_2"
    assert response2_json["is_active"] is True

    # 3. Test schedule date type not found
    response3 = await async_client.get("/schedule_date_types/00000000-0000-0000-0000-000000000000")
    assert response3.status_code == status.HTTP_404_NOT_FOUND

    # 4. Test invalid UUID format
    response4 = await async_client.get("/schedule_date_types/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_schedule_date_type(async_client, seed_schedule_date_types_helper):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"schedule_date_type_name": "Incomplete Type"}
    bad_payload_3 = {"schedule_date_type_name": "Bad Type", "schedule_date_type_code": 12345}  # schedule_date_type_code should be str
    good_payload = {
        "schedule_date_type_name": "New Type",
        "schedule_date_type_code": "new_type"
    }
    
    # Seed another schedule date type directly into test DB
    schedule_date_types = [{"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_4, "schedule_date_type_name": "Another Type", "schedule_date_type_code": "another_type"}]
    await seed_schedule_date_types_helper(schedule_date_types)

    bad_payload_4 = {
        "schedule_date_type_name": "Duplicate Code",
        "schedule_date_type_code": "new_type"  # Duplicate schedule_date_type_code
    }
    bad_payload_5 = {
        "schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_4,  # schedule_date_type_id not allowed in payload
        "schedule_date_type_name": "Duplicate ID Type",
        "schedule_date_type_code": "duplicate_id_type"
    }

    # 1. Test empty payload
    response1 = await async_client.post("/schedule_date_types", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/schedule_date_types", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid data types
    response3 = await async_client.post("/schedule_date_types", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test valid payload
    response4 = await async_client.post("/schedule_date_types", json=good_payload)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert response4_json["schedule_date_type_id"] is not None
    assert response4_json["schedule_date_type_name"] == "New Type"
    assert response4_json["schedule_date_type_code"] == "new_type"
    assert response4_json["is_active"] is True

    # 5. Test duplicate schedule_date_type_code
    response5 = await async_client.post("/schedule_date_types", json=bad_payload_4)
    assert response5.status_code == status.HTTP_409_CONFLICT

    # 6. Test schedule_date_type_id not allowed in payload
    # schedule_date_type_id is not allowed in payload, so this raises 422 Validation Error instead of 409 Conflict
    response6 = await async_client.post("/schedule_date_types", json=bad_payload_5)
    assert response6.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_update_schedule_date_type(async_client, seed_schedule_date_types_helper):
    # Seed schedule date type data directly into test DB
    schedule_date_types = [
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_1, "schedule_date_type_name": "Type 1", "schedule_date_type_code": "type_1"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Type 2", "schedule_date_type_code": "type_2"},
        {"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_3, "schedule_date_type_name": "Type 3", "schedule_date_type_code": "type_3"},
    ]
    await seed_schedule_date_types_helper(schedule_date_types)

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"schedule_date_type_name": 12345}  # schedule_date_type_name should be str
    bad_payload_3 = {"schedule_date_type_name": "Invalid", "schedule_date_type_code": "invalid"}  # schedule_date_type_code is not updatable
    good_payload_full = {
        "schedule_date_type_name": "Updated Type Name",
        "is_active": False
    }
    good_payload_partial_1 = {
        "is_active": False
    }
    good_payload_partial_2 = {
        "schedule_date_type_name": "Partially Updated Type"
    }

    # 1. Test schedule date type not found
    response1 = await async_client.patch("/schedule_date_types/00000000-0000-0000-0000-000000000000", json=good_payload_full)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/schedule_date_types/invalid-uuid-format", json=good_payload_full)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_3}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_3}", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test non-updatable field
    response5 = await async_client.patch(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_3}", json=bad_payload_3)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload to update full record
    response6 = await async_client.patch(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_3}", json=good_payload_full)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["schedule_date_type_name"] == "Updated Type Name"
    assert response6_json["schedule_date_type_code"] == "type_3"
    assert response6_json["is_active"] is False

    # 7. Test valid payload to update partial record (is_active only)
    response7 = await async_client.patch(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_2}", json=good_payload_partial_1)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["schedule_date_type_name"] == "Type 2"
    assert response7_json["schedule_date_type_code"] == "type_2"
    assert response7_json["is_active"] is False 

    # 8. Test valid payload to update partial record (schedule_date_type_name only)
    response8 = await async_client.patch(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_1}", json=good_payload_partial_2)
    assert response8.status_code == status.HTTP_200_OK
    response8_json = response8.json()
    assert response8_json["schedule_date_type_name"] == "Partially Updated Type"
    assert response8_json["schedule_date_type_code"] == "type_1"
    assert response8_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_schedule_date_type(async_client, seed_schedule_date_types_helper):
    # Seed schedule date types data directly into test DB
    schedule_date_types = [{"schedule_date_type_id": SCHEDULE_DATE_TYPE_ID_2, "schedule_date_type_name": "Type 2", "schedule_date_type_code": "type_2"}]
    await seed_schedule_date_types_helper(schedule_date_types)

    # 1. Test schedule date type not found
    response1 = await async_client.delete("/schedule_date_types/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/schedule_date_types/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when schedule date types exist
    response3 = await async_client.delete(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_2}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_2

    # 4. Verify deletion by trying to get it again
    response4 = await async_client.get(f"/schedule_date_types/{SCHEDULE_DATE_TYPE_ID_2}")
    assert response4.status_code == status.HTTP_404_NOT_FOUND