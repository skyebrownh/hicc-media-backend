import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200

MEDIA_ROLE_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
MEDIA_ROLE_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
MEDIA_ROLE_ID_3 = "c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1"
MEDIA_ROLE_ID_4 = "e1fdfd00-e097-415b-c3c7-9579c4c1bb44"

@pytest.mark.asyncio
async def test_get_all_media_roles(async_client, test_db_pool):
    # 1. Test when no media roles exist
    response1 = await async_client.get("/media_roles")
    assert_empty_list_200(response1)

    # Seed media roles data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_name, sort_order, media_role_code)
            VALUES ('Role 1', 1, 'role_1'),
                   ('Role 2', 2, 'role_2'),
                   ('Role 3', 3, 'role_3');
            """
        )

    # 2. Test when media roles exist
    response2 = await async_client.get("/media_roles")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["media_role_name"] == "Role 1"
    assert response2_json[1]["media_role_id"] is not None
    assert response2_json[1]["media_role_code"] == "role_2"
    assert response2_json[2]["description"] is None
    assert response2_json[2]["is_active"] is True

@pytest.mark.asyncio
async def test_get_single_media_role(async_client, test_db_pool):
    # 1. Test when no media roles exist
    response1 = await async_client.get(f"/media_roles/{MEDIA_ROLE_ID_1}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed media roles data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, description, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'Role 1', 'description 1', 1, 'role_1'),
                   ('{MEDIA_ROLE_ID_2}', 'Role 2', 'description 2', 2, 'role_2'),
                   ('{MEDIA_ROLE_ID_3}', 'Role 3', NULL, 3, 'role_3');
            """
        )

    # 2. Test when media roles exist
    response2 = await async_client.get(f"/media_roles/{MEDIA_ROLE_ID_2}")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, dict)
    assert response2_json["media_role_name"] == "Role 2"
    assert response2_json["media_role_code"] == "role_2"
    assert response2_json["description"] == "description 2"
    assert response2_json["is_active"] is True

    # 3. Test media role not found
    response3 = await async_client.get("/media_roles/00000000-0000-0000-0000-000000000000")
    assert response3.status_code == status.HTTP_404_NOT_FOUND

    # 4. Test invalid UUID format
    response4 = await async_client.get("/media_roles/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_media_role(async_client, test_db_pool):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"media_role_name": "Incomplete Role"}
    bad_payload_3 = {"media_role_name": "Bad Role", "sort_order": "not_an_int", "media_role_code": 12345}  # sort_order and media_role_code should be correct types
    good_payload = {
        "media_role_name": "New Role",
        "sort_order": 4,
        "media_role_code": "new_role"
    }
    
    # Seed another media role directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_4}', 'Another Role', 5, 'another_role');
            """
        )

    bad_payload_4 = {
        "media_role_name": "Duplicate Code",
        "sort_order": 6,
        "media_role_code": "new_role"  # Duplicate media_role_code
    }
    bad_payload_5 = {
        "media_role_id": MEDIA_ROLE_ID_4,  # media_role_id not allowed in payload
        "media_role_name": "Duplicate ID Role",
        "sort_order": 7,
        "media_role_code": "duplicate_id_role"
    }

    # 1. Test empty payload
    response1 = await async_client.post("/media_roles", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/media_roles", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid data types
    response3 = await async_client.post("/media_roles", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test valid payload
    response4 = await async_client.post("/media_roles", json=good_payload)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert response4_json["media_role_id"] is not None
    assert response4_json["media_role_name"] == "New Role"
    assert response4_json["media_role_code"] == "new_role"
    assert response4_json["is_active"] is True

    # 5. Test duplicate media_role_code
    response5 = await async_client.post("/media_roles", json=bad_payload_4)
    assert response5.status_code == status.HTTP_409_CONFLICT

    # 6. Test media_role_id not allowed in payload
    # media_role_id is not allowed in payload, so this raises 422 Validation Error instead of 409 Conflict
    response6 = await async_client.post("/media_roles", json=bad_payload_5)
    assert response6.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_update_media_role(async_client, test_db_pool):
    # Seed media role data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, description, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'Role 1', 'description 1', 1, 'role_1'),
                   ('{MEDIA_ROLE_ID_2}', 'Role 2', 'description 2', 2, 'role_2'),
                   ('{MEDIA_ROLE_ID_3}', 'Role 3', 'description 3', 3, 'role_3');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"media_role_name": 12345}  # media_role_name should be str
    bad_payload_3 = {"media_role_name": "Invalid", "media_role_code": "invalid"}  # media_role_code is not updatable
    good_payload_full = {
        "media_role_name": "Updated Role Name",
        "description": "Updated description",
        "sort_order": 100,
        "is_active": False
    }
    good_payload_partial_1 = {
        "is_active": False
    }
    good_payload_partial_2 = {
        "media_role_name": "Partially Updated Role"
    }

    # 1. Test media role not found
    response1 = await async_client.patch("/media_roles/00000000-0000-0000-0000-000000000000", json=good_payload_full)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/media_roles/invalid-uuid-format", json=good_payload_full)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/media_roles/{MEDIA_ROLE_ID_3}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch(f"/media_roles/{MEDIA_ROLE_ID_3}", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test non-updatable field
    response5 = await async_client.patch(f"/media_roles/{MEDIA_ROLE_ID_3}", json=bad_payload_3)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload to update full record
    response6 = await async_client.patch(f"/media_roles/{MEDIA_ROLE_ID_3}", json=good_payload_full)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["media_role_name"] == "Updated Role Name"
    assert response6_json["description"] == "Updated description"
    assert response6_json["media_role_code"] == "role_3"
    assert response6_json["is_active"] is False

    # 7. Test valid payload to update partial record (is_active only)
    response7 = await async_client.patch(f"/media_roles/{MEDIA_ROLE_ID_2}", json=good_payload_partial_1)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["media_role_name"] == "Role 2"
    assert response7_json["description"] == "description 2"
    assert response7_json["media_role_code"] == "role_2"
    assert response7_json["is_active"] is False 

    # 8. Test valid payload to update partial record (media_role_name only)
    response8 = await async_client.patch(f"/media_roles/{MEDIA_ROLE_ID_1}", json=good_payload_partial_2)
    assert response8.status_code == status.HTTP_200_OK
    response8_json = response8.json()
    assert response8_json["media_role_name"] == "Partially Updated Role"
    assert response8_json["description"] == "description 1"
    assert response8_json["media_role_code"] == "role_1"
    assert response8_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_media_role(async_client, test_db_pool):
    # Seed media roles data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'Role 1', 1, 'role_1'),
                   ('{MEDIA_ROLE_ID_2}', 'Role 2', 2, 'role_2'),
                   ('{MEDIA_ROLE_ID_3}', 'Role 3', 3, 'role_3');
            """
        )

    # 1. Test media role not found
    response1 = await async_client.delete("/media_roles/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/media_roles/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when media roles exist
    response3 = await async_client.delete(f"/media_roles/{MEDIA_ROLE_ID_2}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["media_role_id"] == MEDIA_ROLE_ID_2

    # 4. Verify deletion by trying to get it again
    response4 = await async_client.get(f"/media_roles/{MEDIA_ROLE_ID_2}")
    assert response4.status_code == status.HTTP_404_NOT_FOUND