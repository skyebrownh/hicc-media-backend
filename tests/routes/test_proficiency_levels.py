import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200

PROFICIENCY_LEVEL_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
PROFICIENCY_LEVEL_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
PROFICIENCY_LEVEL_ID_3 = "c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1"
PROFICIENCY_LEVEL_ID_4 = "e1fdfd00-e097-415b-c3c7-9579c4c1bb44"

@pytest.mark.asyncio
async def test_get_all_proficiency_levels(async_client, test_db_pool):
    # 1. Test when no proficiency levels exist
    response1 = await async_client.get("/proficiency_levels")
    assert_empty_list_200(response1)

    # Seed proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_name, proficiency_level_number, proficiency_level_code)
            VALUES ('Level 1', 1, 'level_1'),
                   ('Level 2', 2, 'level_2'),
                   ('Level 3', 3, 'level_3');
            """
        )

    # 2. Test when proficiency levels exist
    response2 = await async_client.get("/proficiency_levels")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["proficiency_level_name"] == "Level 1"
    assert response2_json[1]["proficiency_level_id"] is not None
    assert response2_json[1]["proficiency_level_code"] == "level_2"
    assert response2_json[1]["proficiency_level_number"] == 2
    assert response2_json[2]["is_active"] is True
    assert response2_json[2]["is_assignable"] is False

@pytest.mark.asyncio
async def test_get_single_proficiency_level(async_client, test_db_pool):
    # 1. Test when no proficiency levels exist
    response1 = await async_client.get(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code)
            VALUES ('{PROFICIENCY_LEVEL_ID_1}', 'Level 1', 1, 'level_1'),
                   ('{PROFICIENCY_LEVEL_ID_2}', 'Level 2', 2, 'level_2'),
                   ('{PROFICIENCY_LEVEL_ID_3}', 'Level 3', 3, 'level_3');
            """
        )

    # 2. Test when proficiency levels exist
    response2 = await async_client.get(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_2}")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, dict)
    assert response2_json["proficiency_level_name"] == "Level 2"
    assert response2_json["proficiency_level_number"] == 2
    assert response2_json["proficiency_level_code"] == "level_2"
    assert response2_json["is_active"] is True
    assert response2_json["is_assignable"] is False

    # 3. Test proficiency level not found
    response3 = await async_client.get("/proficiency_levels/00000000-0000-0000-0000-000000000000")
    assert response3.status_code == status.HTTP_404_NOT_FOUND

    # 4. Test invalid UUID format
    response4 = await async_client.get("/proficiency_levels/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_proficiency_level(async_client, test_db_pool):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"proficiency_level_name": "Incomplete Level"}
    bad_payload_3 = {"proficiency_level_name": "Bad Level", "proficiency_level_number": "not_an_int", "proficiency_level_code": 12345}  # proficiency_level_number and proficiency_level_code should be correct types
    good_payload = {
        "proficiency_level_name": "New Level",
        "proficiency_level_code": "new_level"
    }
    
    # Seed another proficiency level directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code)
            VALUES ('{PROFICIENCY_LEVEL_ID_4}', 'Another Level', 5, 'another_level');
            """
        )

    bad_payload_4 = {
        "proficiency_level_name": "Duplicate Code",
        "proficiency_level_number": 6,
        "proficiency_level_code": "new_level"  # Duplicate proficiency_level_code
    }
    bad_payload_5 = {
        "proficiency_level_id": PROFICIENCY_LEVEL_ID_4,  # proficiency_level_id not allowed in payload
        "proficiency_level_name": "Duplicate ID Level",
        "proficiency_level_number": 7,
        "proficiency_level_code": "duplicate_id_level"
    }

    # 1. Test empty payload
    response1 = await async_client.post("/proficiency_levels", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/proficiency_levels", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid data types
    response3 = await async_client.post("/proficiency_levels", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test valid payload
    response4 = await async_client.post("/proficiency_levels", json=good_payload)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert response4_json["proficiency_level_id"] is not None
    assert response4_json["proficiency_level_name"] == "New Level"
    assert response4_json["proficiency_level_number"] is None
    assert response4_json["proficiency_level_code"] == "new_level"
    assert response4_json["is_active"] is True
    assert response4_json["is_assignable"] is False

    # 5. Test duplicate proficiency_level_code
    response5 = await async_client.post("/proficiency_levels", json=bad_payload_4)
    assert response5.status_code == status.HTTP_409_CONFLICT

    # 6. Test proficiency_level_id not allowed in payload
    # proficiency_level_id is not allowed in payload, so this raises 422 Validation Error instead of 409 Conflict
    response6 = await async_client.post("/proficiency_levels", json=bad_payload_5)
    assert response6.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_update_proficiency_level(async_client, test_db_pool):
    # Seed proficiency level data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code)
            VALUES ('{PROFICIENCY_LEVEL_ID_1}', 'Level 1', 1, 'level_1'),
                   ('{PROFICIENCY_LEVEL_ID_2}', 'Level 2', 2, 'level_2'),
                   ('{PROFICIENCY_LEVEL_ID_3}', 'Level 3', 3, 'level_3');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"proficiency_level_name": 12345}  # proficiency_level_name should be str
    bad_payload_3 = {"proficiency_level_name": "Invalid", "proficiency_level_code": "invalid"}  # proficiency_level_code is not updatable
    good_payload_full = {
        "proficiency_level_name": "Updated Level Name",
        "proficiency_level_number": 100,
        "is_active": False,
        "is_assignable": True
    }
    good_payload_partial_1 = {
        "is_active": False
    }
    good_payload_partial_2 = {
        "proficiency_level_name": "Partially Updated Level"
    }

    # 1. Test proficiency level not found
    response1 = await async_client.patch("/proficiency_levels/00000000-0000-0000-0000-000000000000", json=good_payload_full)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/proficiency_levels/invalid-uuid-format", json=good_payload_full)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test non-updatable field
    response5 = await async_client.patch(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", json=bad_payload_3)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload to update full record
    response6 = await async_client.patch(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", json=good_payload_full)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["proficiency_level_name"] == "Updated Level Name"
    assert response6_json["proficiency_level_code"] == "level_3"
    assert response6_json["proficiency_level_number"] == 100
    assert response6_json["is_active"] is False
    assert response6_json["is_assignable"] is True

    # 7. Test valid payload to update partial record (is_active only)
    response7 = await async_client.patch(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_2}", json=good_payload_partial_1)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["proficiency_level_name"] == "Level 2"
    assert response7_json["proficiency_level_code"] == "level_2"
    assert response7_json["is_active"] is False 

    # 8. Test valid payload to update partial record (proficiency_level_name only)
    response8 = await async_client.patch(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}", json=good_payload_partial_2)
    assert response8.status_code == status.HTTP_200_OK
    response8_json = response8.json()
    assert response8_json["proficiency_level_name"] == "Partially Updated Level"
    assert response8_json["proficiency_level_code"] == "level_1"
    assert response8_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_proficiency_level(async_client, test_db_pool):
    # Seed proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code)
            VALUES ('{PROFICIENCY_LEVEL_ID_1}', 'Level 1', 1, 'level_1'),
                   ('{PROFICIENCY_LEVEL_ID_2}', 'Level 2', 2, 'level_2'),
                   ('{PROFICIENCY_LEVEL_ID_3}', 'Level 3', 3, 'level_3');
            """
        )

    # 1. Test proficiency level not found
    response1 = await async_client.delete("/proficiency_levels/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/proficiency_levels/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when proficiency levels exist
    response3 = await async_client.delete(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_2}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["proficiency_level_name"] == "Level 2"
    assert response3_json["proficiency_level_code"] == "level_2"
    assert response3_json["is_active"] is True