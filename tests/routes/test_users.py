import pytest
import pytest_asyncio
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, insert_users

# Test data constants
USER_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
USER_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
USER_ID_3 = "c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1"
USER_ID_4 = "e1fdfd00-e097-415b-c3c7-9579c4c1bb44"

@pytest_asyncio.fixture
async def seed_users_helper(test_db_pool):
    """Helper fixture to seed users in the database"""
    async def seed_users(users: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_users(users))
    return seed_users

@pytest.mark.asyncio
async def test_get_all_users(async_client, seed_users_helper):
    # 1. Test when no users exist
    response1 = await async_client.get("/users")
    assert_empty_list_200(response1)

    # Seed users data directly into test DB
    users = [
        {"first_name": "Alice", "last_name": "Smith", "phone": "555-1111", "email": "alice@example.com"},
        {"first_name": "Bob", "last_name": "Jones", "phone": "555-2222", "email": "bob@example.com"},
        {"first_name": "Carol", "last_name": "Lee", "phone": "555-3333", "email": None},
    ]
    await seed_users_helper(users)

    # 2. Test when users exist
    response2 = await async_client.get("/users")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["first_name"] == "Alice"
    assert response2_json[1]["user_id"] is not None
    assert response2_json[1]["email"] == "bob@example.com"
    assert response2_json[2]["phone"] == "555-3333"
    assert response2_json[2]["is_active"] is True

@pytest.mark.asyncio
async def test_get_single_user(async_client, seed_users_helper):
    # 1. Test when no users exist
    response1 = await async_client.get(f"/users/{USER_ID_1}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed users data directly into test DB
    users = [
        {"user_id": USER_ID_1, "first_name": "Alice", "last_name": "Smith", "phone": "555-1111", "email": "alice@example.com"},
        {"user_id": USER_ID_2, "first_name": "Bob", "last_name": "Jones", "phone": "555-2222", "email": "bob@example.com"},
        {"user_id": USER_ID_3, "first_name": "Carol", "last_name": "Lee", "phone": "555-3333", "email": None},
    ]
    await seed_users_helper(users)

    # 2. Test when users exist
    response2 = await async_client.get(f"/users/{USER_ID_2}")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, dict)
    assert response2_json["first_name"] == "Bob"
    assert response2_json["phone"] == "555-2222"
    assert response2_json["email"] == "bob@example.com"
    assert response2_json["last_name"] == "Jones"
    assert response2_json["is_active"] is True

    # 3. Test user not found
    response3 = await async_client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response3.status_code == status.HTTP_404_NOT_FOUND

    # 4. Test invalid UUID format
    response4 = await async_client.get("/users/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_user(async_client, seed_users_helper):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"first_name": "Incomplete"}
    bad_payload_3 = {"first_name": 123, "last_name": True, "phone": 555, "email": 999}  # wrong types
    good_payload = {
        "first_name": "New",
        "last_name": "User",
        "phone": "555-4444",
        "email": "newuser@example.com"
    }

    # Seed another user directly into test DB
    users = [{"user_id": USER_ID_4, "first_name": "Another", "last_name": "User", "phone": "555-5555", "email": "another@example.com"}]
    await seed_users_helper(users)

    bad_payload_4 = {
        "user_id": USER_ID_4,  # Not allowed in payload
        "first_name": "Duplicate",
        "last_name": "ID",
        "phone": "555-6666",
        "email": "dup@example.com"
    }

    # 1. Test empty payload
    response1 = await async_client.post("/users", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/users", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid data types
    response3 = await async_client.post("/users", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test valid payload
    response4 = await async_client.post("/users", json=good_payload)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert response4_json["user_id"] is not None
    assert response4_json["first_name"] == "New"
    assert response4_json["last_name"] == "User"
    assert response4_json["is_active"] is True

    # 5. Test user_id in payload (should be forbidden)
    response5 = await async_client.post("/users", json=bad_payload_4)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_update_user(async_client, seed_users_helper):
    # Seed user data directly into test DB
    users = [
        {"user_id": USER_ID_1, "first_name": "Alice", "last_name": "Smith", "phone": "555-1111", "email": "alice@example.com"},
        {"user_id": USER_ID_2, "first_name": "Bob", "last_name": "Jones", "phone": "555-2222", "email": "bob@example.com"},
        {"user_id": USER_ID_3, "first_name": "Carol", "last_name": "Lee", "phone": "555-3333", "email": None},
    ]
    await seed_users_helper(users)

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"first_name": 12345}  # first_name should be str
    bad_payload_3 = {"user_id": "not-allowed"}  # user_id is not updatable
    good_payload_full = {
        "first_name": "Updated",
        "last_name": "User",
        "phone": "555-7777",
        "email": "updated@example.com",
        "is_active": False
    }
    good_payload_partial_1 = {
        "is_active": False
    }
    good_payload_partial_2 = {
        "first_name": "Partially Updated"
    }

    # 1. Test user not found
    response1 = await async_client.patch("/users/00000000-0000-0000-0000-000000000000", json=good_payload_full)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/users/invalid-uuid-format", json=good_payload_full)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/users/{USER_ID_3}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch(f"/users/{USER_ID_3}", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test non-updatable field
    response5 = await async_client.patch(f"/users/{USER_ID_3}", json=bad_payload_3)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload to update full record
    response6 = await async_client.patch(f"/users/{USER_ID_3}", json=good_payload_full)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["first_name"] == "Updated"
    assert response6_json["last_name"] == "User"
    assert response6_json["phone"] == "555-7777"
    assert response6_json["email"] == "updated@example.com"
    assert response6_json["is_active"] is False

    # 7. Test valid payload to update partial record (is_active only)
    response7 = await async_client.patch(f"/users/{USER_ID_2}", json=good_payload_partial_1)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["first_name"] == "Bob"
    assert response7_json["last_name"] == "Jones"
    assert response7_json["is_active"] is False

    # 8. Test valid payload to update partial record (first_name only)
    response8 = await async_client.patch(f"/users/{USER_ID_1}", json=good_payload_partial_2)
    assert response8.status_code == status.HTTP_200_OK
    response8_json = response8.json()
    assert response8_json["first_name"] == "Partially Updated"
    assert response8_json["last_name"] == "Smith"
    assert response8_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_user(async_client, seed_users_helper):
    # Seed users data directly into test DB
    users = [
        {"user_id": USER_ID_1, "first_name": "Alice", "last_name": "Smith", "phone": "555-1111", "email": "alice@example.com"},
        {"user_id": USER_ID_2, "first_name": "Bob", "last_name": "Jones", "phone": "555-2222", "email": "bob@example.com"},
        {"user_id": USER_ID_3, "first_name": "Carol", "last_name": "Lee", "phone": "555-3333", "email": None},
    ]
    await seed_users_helper(users)

    # 1. Test user not found
    response1 = await async_client.delete("/users/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/users/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when users exist
    response3 = await async_client.delete(f"/users/{USER_ID_2}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["user_id"] == USER_ID_2

    # 4. Verify deletion by trying to get it again
    response4 = await async_client.get(f"/users/{USER_ID_2}")
    assert response4.status_code == status.HTTP_404_NOT_FOUND