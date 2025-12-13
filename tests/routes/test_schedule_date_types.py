import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_get_all_schedule_date_types(async_client, test_db_pool):
    # 1. Test when no schedule date types exist
    response1 = await async_client.get("/schedule_date_types")
    assert response1.status_code == status.HTTP_200_OK
    assert isinstance(response1.json(), list)
    assert len(response1.json()) == 0
    assert response1.json() == []

    # Seed schedule date types data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO schedule_date_types (schedule_date_type_name, schedule_date_type_code)
            VALUES ('Type 1', 'type_1'),
                   ('Type 2', 'type_2'),
                   ('Type 3', 'type_3');
            """
        )

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
async def test_get_single_schedule_date_type(async_client, test_db_pool):
    # 1. Test when no schedule date types exist
    response1 = await async_client.get("/schedule_date_types/58a6929c-f40d-4363-984c-4c221f41d4f0")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed schedule date types data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('58a6929c-f40d-4363-984c-4c221f41d4f0', 'Type 1', 'type_1'),
                   ('fb4d832f-6a45-473e-b9e2-c0495938d005', 'Type 2', 'type_2'),
                   ('c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1', 'Type 3', 'type_3');
            """
        )

    # 2. Test when schedule date types exist
    response2 = await async_client.get("/schedule_date_types/fb4d832f-6a45-473e-b9e2-c0495938d005")
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
async def test_insert_schedule_date_type(async_client, test_db_pool):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"schedule_date_type_name": "Incomplete Type"}
    bad_payload_3 = {"schedule_date_type_name": "Bad Type", "schedule_date_type_code": 12345}  # schedule_date_type_code should be str
    good_payload = {
        "schedule_date_type_name": "New Type",
        "schedule_date_type_code": "new_type"
    }
    
    # Seed another schedule date type directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('f8d3e340-9563-4de1-9146-675a8436242e', 'Another Type', 'another_type');
            """
        )

    bad_payload_4 = {
        "schedule_date_type_name": "Duplicate Code",
        "schedule_date_type_code": "new_type"  # Duplicate schedule_date_type_code
    }
    bad_payload_5 = {
        "schedule_date_type_id": "f8d3e340-9563-4de1-9146-675a8436242e",  # schedule_date_type_id not allowed in payload
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
async def test_update_schedule_date_type(async_client, test_db_pool):
    # Seed schedule date type data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('58a6929c-f40d-4363-984c-4c221f41d4f0', 'Type 1', 'type_1'),
                   ('fb4d832f-6a45-473e-b9e2-c0495938d005', 'Type 2', 'type_2'),
                   ('c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1', 'Type 3', 'type_3');
            """
        )

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
    response3 = await async_client.patch("/schedule_date_types/c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch("/schedule_date_types/c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test non-updatable field
    response5 = await async_client.patch("/schedule_date_types/c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1", json=bad_payload_3)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload to update full record
    response6 = await async_client.patch("/schedule_date_types/c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1", json=good_payload_full)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["schedule_date_type_name"] == "Updated Type Name"
    assert response6_json["schedule_date_type_code"] == "type_3"
    assert response6_json["is_active"] is False

    # 7. Test valid payload to update partial record (is_active only)
    response7 = await async_client.patch("/schedule_date_types/fb4d832f-6a45-473e-b9e2-c0495938d005", json=good_payload_partial_1)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["schedule_date_type_name"] == "Type 2"
    assert response7_json["schedule_date_type_code"] == "type_2"
    assert response7_json["is_active"] is False 

    # 8. Test valid payload to update partial record (schedule_date_type_name only)
    response8 = await async_client.patch("/schedule_date_types/58a6929c-f40d-4363-984c-4c221f41d4f0", json=good_payload_partial_2)
    assert response8.status_code == status.HTTP_200_OK
    response8_json = response8.json()
    assert response8_json["schedule_date_type_name"] == "Partially Updated Type"
    assert response8_json["schedule_date_type_code"] == "type_1"
    assert response8_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_schedule_date_type(async_client, test_db_pool):
    # Seed schedule date types data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('58a6929c-f40d-4363-984c-4c221f41d4f0', 'Type 1', 'type_1'),
                   ('fb4d832f-6a45-473e-b9e2-c0495938d005', 'Type 2', 'type_2'),
                   ('c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1', 'Type 3', 'type_3');
            """
        )

    # 1. Test schedule date type not found
    response1 = await async_client.delete("/schedule_date_types/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/schedule_date_types/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when schedule date types exist
    response3 = await async_client.delete("/schedule_date_types/fb4d832f-6a45-473e-b9e2-c0495938d005")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["schedule_date_type_name"] == "Type 2"
    assert response3_json["schedule_date_type_code"] == "type_2"
    assert response3_json["is_active"] is True