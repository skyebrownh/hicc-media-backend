import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.utils.constants import BAD_ID_0000, USER_ID_1, USER_ID_2, USER_ID_3, USER_ID_4

# =============================
# DATA FIXTURES
# =============================
@pytest.fixture
def test_users_data():
    """Fixture providing array of test user data"""
    return [
        {"user_id": USER_ID_1, "first_name": "Alice", "last_name": "Smith", "phone": "555-1111", "email": "alice@example.com"},
        {"user_id": USER_ID_2, "first_name": "Bob", "last_name": "Jones", "phone": "555-2222", "email": "bob@example.com"},
        {"user_id": USER_ID_3, "first_name": "Carol", "last_name": "Lee", "phone": "555-3333", "email": None},
        {"user_id": USER_ID_4, "first_name": "Another", "last_name": "User", "phone": "555-5555", "email": "another@example.com"},
    ]

# =============================
# GET ALL USERS
# =============================
@pytest.mark.asyncio
async def test_get_all_users_none_exist(async_client):
    """Test when no users exist returns empty list"""
    response = await async_client.get("/users")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_users_success(async_client, seed_users, test_users_data):
    """Test getting all users after inserting a variety"""
    await seed_users(test_users_data[:3])

    response = await async_client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["first_name"] == "Alice"
    assert response_json[1]["user_id"] is not None
    assert response_json[1]["email"] == "bob@example.com"
    assert response_json[2]["phone"] == "555-3333"
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE USER
# =============================
@pytest.mark.parametrize("user_id, expected_status", [
    # User not present
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_user_error_cases(async_client, user_id, expected_status):
    """Test GET single user error cases (404 and 422)"""
    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_user_success(async_client, seed_users, test_users_data):
    """Test GET single user success case"""
    await seed_users([test_users_data[1]])
    
    response = await async_client.get(f"/users/{USER_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["first_name"] == "Bob"
    assert response_json["phone"] == "555-2222"
    assert response_json["email"] == "bob@example.com"
    assert response_json["last_name"] == "Jones"
    assert response_json["is_active"] is True

# =============================
# INSERT USER
# =============================
@pytest.mark.parametrize("user_indices, payload, expected_status", [
    # empty payload
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields
    ([], {"first_name": "Incomplete"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid data types
    ([], {"first_name": 123, "last_name": True, "phone": 555, "email": 999}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # user_id not allowed in payload
    ([3], {"user_id": USER_ID_4, "first_name": "Duplicate", "last_name": "ID", "phone": "555-6666", "email": "dup@example.com"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_insert_user_error_cases(async_client, seed_users, test_users_data, user_indices, payload, expected_status):
    """Test INSERT user error cases (422)"""
    users = [test_users_data[i] for i in user_indices] if user_indices else []
    await seed_users(users)
    
    response = await async_client.post("/users", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_user_success(async_client):
    """Test valid user insertion"""
    response = await async_client.post("/users", json={
        "first_name": "New",
        "last_name": "User",
        "phone": "555-4444",
        "email": "newuser@example.com"
    })
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["user_id"] is not None
    assert response_json["first_name"] == "New"
    assert response_json["last_name"] == "User"
    assert response_json["is_active"] is True

# =============================
# UPDATE USER
# =============================
@pytest.mark.parametrize("user_indices, user_path, payload, expected_status", [
    # user not found
    ([], f"/users/{BAD_ID_0000}", {"first_name": "Updated", "last_name": "User", "phone": "555-7777", "email": "updated@example.com", "is_active": False}, status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ([0], "/users/invalid-uuid-format", {"first_name": "Updated", "last_name": "User", "phone": "555-7777", "email": "updated@example.com", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    ([2], f"/users/{USER_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
    # invalid data types
    ([2], f"/users/{USER_ID_3}", {"first_name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # non-updatable field
    ([2], f"/users/{USER_ID_3}", {"user_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_update_user_error_cases(async_client, seed_users, test_users_data, user_indices, user_path, payload, expected_status):
    """Test UPDATE user error cases (400, 404, and 422)"""
    users = [test_users_data[i] for i in user_indices] if user_indices else []
    await seed_users(users)
    
    response = await async_client.patch(user_path, json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("user_id, payload, expected_fields, unchanged_fields", [
    # full update
    (
        USER_ID_3,
        {"first_name": "Updated", "last_name": "User", "phone": "555-7777", "email": "updated@example.com", "is_active": False},
        {"first_name": "Updated", "last_name": "User", "phone": "555-7777", "email": "updated@example.com", "is_active": False},
        {}
    ),
    # partial update (is_active only)
    (
        USER_ID_2,
        {"is_active": False},
        {"is_active": False},
        {"first_name": "Bob", "last_name": "Jones"}
    ),
    # partial update (first_name only)
    (
        USER_ID_1,
        {"first_name": "Partially Updated"},
        {"first_name": "Partially Updated"},
        {"last_name": "Smith", "is_active": True}
    ),
])
@pytest.mark.asyncio
async def test_update_user_success(async_client, seed_users, test_users_data, user_id, payload, expected_fields, unchanged_fields):
    """Test valid user updates"""
    await seed_users(test_users_data[:3])
    
    response = await async_client.patch(f"/users/{user_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value
    for field, expected_value in unchanged_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE USER
# =============================
@pytest.mark.parametrize("user_indices, user_path, expected_status", [
    # user not found
    ([], f"/users/{BAD_ID_0000}", status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ([0], "/users/invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_user_error_cases(async_client, seed_users, test_users_data, user_indices, user_path, expected_status):
    """Test DELETE user error cases (404 and 422)"""
    users = [test_users_data[i] for i in user_indices] if user_indices else []
    await seed_users(users)
    
    response = await async_client.delete(user_path)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_user_success(async_client, seed_users, test_users_data):
    """Test successful user deletion with verification"""
    await seed_users([test_users_data[1]])

    # Test successful deletion
    response = await async_client.delete(f"/users/{USER_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["user_id"] == USER_ID_2

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/users/{USER_ID_2}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND
