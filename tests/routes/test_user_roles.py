import pytest
from uuid import UUID
from fastapi import status
from app.db.queries import insert_all_roles_for_user, insert_all_users_for_role
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, USER_ID_1, USER_ID_2, USER_ID_3, MEDIA_ROLE_ID_1, MEDIA_ROLE_ID_2, MEDIA_ROLE_ID_3,
    PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2
)

# =============================
# GET ROLES FOR USER
# =============================
@pytest.mark.parametrize("user_id, expected_status", [
    # User not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_roles_for_user_error_cases(async_client, user_id, expected_status):
    """Test GET roles for user error cases (404, 422)"""
    response = await async_client.get(f"/users/{user_id}/roles")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_roles_for_user_none_exist(async_client, seed_users, test_users_data):
    """Test GET roles for user when none exist returns empty list"""
    await seed_users([test_users_data[2]])
    response = await async_client.get(f"/users/{USER_ID_3}/roles")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_roles_for_user_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data):
    """Test GET roles for user success case"""
    await seed_users([test_users_data[0]])
    await seed_media_roles(test_media_roles_data[:2])
    await seed_proficiency_levels(test_proficiency_levels_data[:2])
    await seed_user_roles(test_user_roles_data[:2])

    response = await async_client.get(f"/users/{USER_ID_1}/roles")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2
    assert response_json[0]["user_role_id"] is not None
    assert response_json[0]["user_id"] == USER_ID_1
    assert response_json[0]["media_role_id"] == MEDIA_ROLE_ID_1
    assert response_json[1]["user_id"] == USER_ID_1
    assert response_json[1]["media_role_id"] == MEDIA_ROLE_ID_2

# =============================
# GET USERS FOR ROLE
# =============================
@pytest.mark.parametrize("role_id, expected_status", [
    # Role not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_users_for_role_error_cases(async_client, role_id, expected_status):
    """Test GET users for role error cases (404, 422)"""
    response = await async_client.get(f"/roles/{role_id}/users")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_users_for_role_none_exist(async_client, seed_users, seed_media_roles, seed_proficiency_levels, test_users_data, test_media_roles_data, test_proficiency_levels_data):
    """Test GET users for role when none exist returns empty list"""
    await seed_users(test_users_data[:3])
    await seed_media_roles(test_media_roles_data[:3])
    await seed_proficiency_levels([test_proficiency_levels_data[0]])

    response = await async_client.get(f"/roles/{MEDIA_ROLE_ID_3}/users")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_users_for_role_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data):
    """Test GET users for role success case"""
    await seed_users(test_users_data[:2])
    await seed_media_roles([test_media_roles_data[0]])
    await seed_proficiency_levels([test_proficiency_levels_data[0]])
    await seed_user_roles([test_user_roles_data[0], test_user_roles_data[2]])

    response = await async_client.get(f"/roles/{MEDIA_ROLE_ID_1}/users")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2
    assert response_json[0]["user_role_id"] is not None
    assert response_json[0]["media_role_id"] == MEDIA_ROLE_ID_1
    assert response_json[0]["user_id"] == USER_ID_1
    assert response_json[1]["media_role_id"] == MEDIA_ROLE_ID_1
    assert response_json[1]["user_id"] == USER_ID_2

# =============================
# GET SINGLE USER ROLE
# =============================
@pytest.mark.parametrize("user_id, role_id, expected_status", [
    # User role not found
    (USER_ID_1, MEDIA_ROLE_ID_2, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format for user_id
    ("invalid-uuid-format", MEDIA_ROLE_ID_1, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Invalid UUID format for role_id
    (USER_ID_1, "invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_user_role_error_cases(async_client, user_id, role_id, expected_status):
    """Test GET single user role error cases (404 and 422)"""
    response = await async_client.get(f"/users/{user_id}/roles/{role_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_user_role_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data):
    """Test GET single user role success case"""
    await seed_users([test_users_data[0]])
    await seed_media_roles([test_media_roles_data[0]])
    await seed_proficiency_levels([test_proficiency_levels_data[0]])
    await seed_user_roles([test_user_roles_data[0]])

    response = await async_client.get(f"/users/{USER_ID_1}/roles/{MEDIA_ROLE_ID_1}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["user_id"] == USER_ID_1
    assert response_json["media_role_id"] == MEDIA_ROLE_ID_1
    assert response_json["proficiency_level_id"] == PROFICIENCY_LEVEL_ID_1

# =============================
# INSERT USER ROLE
# =============================
@pytest.mark.parametrize("user_indices, role_indices, proficiency_indices, user_role_indices, payload, expected_status", [
    # empty payload
    ([], [], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields
    ([], [], [], [], {"user_id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields (proficiency_level_id)
    ([], [], [], [], {"user_id": USER_ID_2, "media_role_id": MEDIA_ROLE_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid UUID format
    ([], [], [], [], {"user_id": "invalid-uuid", "media_role_id": MEDIA_ROLE_ID_2, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # duplicate user_role
    ([0], [0], [0], [0], {"user_id": USER_ID_1, "media_role_id": MEDIA_ROLE_ID_1, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1}, status.HTTP_409_CONFLICT),
    # extra fields not allowed
    ([], [], [], [], {"user_id": USER_ID_2, "media_role_id": MEDIA_ROLE_ID_2, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1, "user_role_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # foreign key violation (user doesn't exist)
    ([], [1], [0], [], {"user_id": BAD_ID_0000, "media_role_id": MEDIA_ROLE_ID_2, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1}, status.HTTP_404_NOT_FOUND),
    # foreign key violation (role doesn't exist)
    ([1], [], [0], [], {"user_id": USER_ID_2, "media_role_id": BAD_ID_0000, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1}, status.HTTP_404_NOT_FOUND),
    # foreign key violation (proficiency doesn't exist)
    ([0], [1], [], [], {"user_id": USER_ID_1, "media_role_id": MEDIA_ROLE_ID_2, "proficiency_level_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_insert_user_role_error_cases(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data, user_indices, role_indices, proficiency_indices, user_role_indices, payload, expected_status):
    """Test INSERT user role error cases (422, 409, and 404)"""
    await conditional_seed(user_indices, test_users_data, seed_users)
    await conditional_seed(role_indices, test_media_roles_data, seed_media_roles)
    await conditional_seed(proficiency_indices, test_proficiency_levels_data, seed_proficiency_levels)
    await conditional_seed(user_role_indices, test_user_roles_data, seed_user_roles)
    response = await async_client.post("/user_roles", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_user_role_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, test_users_data, test_media_roles_data, test_proficiency_levels_data):
    """Test valid user role insertion"""
    await seed_users([test_users_data[1]])
    await seed_media_roles([test_media_roles_data[1]])
    await seed_proficiency_levels([test_proficiency_levels_data[0]])
    
    response = await async_client.post("/user_roles", json={
        "user_id": USER_ID_2,
        "media_role_id": MEDIA_ROLE_ID_2,
        "proficiency_level_id": PROFICIENCY_LEVEL_ID_1
    })
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["user_role_id"] is not None
    assert response_json["user_id"] == USER_ID_2
    assert response_json["media_role_id"] == MEDIA_ROLE_ID_2
    assert response_json["proficiency_level_id"] == PROFICIENCY_LEVEL_ID_1

# =============================
# INSERT ALL ROLES FOR USER
# =============================
@pytest.mark.asyncio
async def test_insert_all_roles_for_user_missing_untrained(seed_users, seed_media_roles, test_db_pool, test_users_data, test_media_roles_data):
    """Test inserting all roles for a user when 'untrained' proficiency level doesn't exist"""
    await seed_users([test_users_data[0]])
    await seed_media_roles([test_media_roles_data[0], test_media_roles_data[1]])

    async with test_db_pool.acquire() as conn:
        with pytest.raises(ValueError) as exc_info:
            await insert_all_roles_for_user(conn, user_id=UUID(USER_ID_1))
        assert "Default proficiency level 'untrained' not found" in str(exc_info.value)

@pytest.mark.parametrize("user_id, expected_status", [
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
    # User doesn't exist
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_insert_all_roles_for_user_error_cases(async_client, user_id, expected_status):
    """Test INSERT all roles for user error cases (422 and 404)"""
    response = await async_client.post(f"/users/{user_id}/roles")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_all_roles_for_user_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, test_users_data, test_media_roles_data, test_proficiency_levels_data):
    """Test inserting all roles for a user"""
    await seed_users([test_users_data[0]])
    await seed_media_roles(test_media_roles_data[:2])
    await seed_proficiency_levels([test_proficiency_levels_data[2]])

    response1 = await async_client.post(f"/users/{USER_ID_1}/roles")
    assert response1.status_code == status.HTTP_201_CREATED
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert response1_json[0]["user_id"] == USER_ID_1
    assert response1_json[0]["media_role_id"] == MEDIA_ROLE_ID_1
    assert response1_json[1]["user_id"] == USER_ID_1
    assert response1_json[1]["media_role_id"] == MEDIA_ROLE_ID_2

# =============================
# INSERT ALL USERS FOR ROLE
# =============================
@pytest.mark.asyncio
async def test_insert_all_users_for_role_missing_untrained(seed_users, seed_media_roles, test_db_pool, test_users_data, test_media_roles_data):
    """Test inserting all users for a role when 'untrained' proficiency level doesn't exist"""
    await seed_users(test_users_data[:1])
    await seed_media_roles([test_media_roles_data[0]])

    async with test_db_pool.acquire() as conn:
        with pytest.raises(ValueError) as exc_info:
            await insert_all_users_for_role(conn, role_id=UUID(MEDIA_ROLE_ID_1))
        assert "Default proficiency level 'untrained' not found" in str(exc_info.value)

@pytest.mark.parametrize("role_id, expected_status", [
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Role doesn't exist
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_insert_all_users_for_role_error_cases(async_client, role_id, expected_status):
    """Test INSERT all users for role error cases (422 and 404)"""
    response = await async_client.post(f"/roles/{role_id}/users")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_all_users_for_role_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, test_users_data, test_media_roles_data, test_proficiency_levels_data):
    """Test inserting all users for a role"""
    await seed_users(test_users_data[:2])
    await seed_media_roles([test_media_roles_data[0]])
    await seed_proficiency_levels([test_proficiency_levels_data[2]])

    response1 = await async_client.post(f"/roles/{MEDIA_ROLE_ID_1}/users")
    assert response1.status_code == status.HTTP_201_CREATED
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert response1_json[0]["media_role_id"] == MEDIA_ROLE_ID_1
    assert response1_json[0]["user_id"] == USER_ID_1
    assert response1_json[1]["media_role_id"] == MEDIA_ROLE_ID_1
    assert response1_json[1]["user_id"] == USER_ID_2

# =============================
# UPDATE USER ROLE
# =============================
@pytest.mark.parametrize("user_indices, role_indices, proficiency_indices, user_role_indices, user_id, role_id, payload, expected_status", [
    # user role not found
    ([], [], [], [], USER_ID_1, MEDIA_ROLE_ID_2, {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_404_NOT_FOUND),
    # invalid UUID format for user_id
    ([], [], [], [], "invalid-uuid-format", MEDIA_ROLE_ID_1, {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid UUID format for role_id
    ([], [], [], [], USER_ID_1, "invalid-uuid-format", {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    ([], [], [], [], USER_ID_1, MEDIA_ROLE_ID_1, {}, status.HTTP_400_BAD_REQUEST),
    # invalid UUID format in payload
    ([], [], [], [], USER_ID_1, MEDIA_ROLE_ID_1, {"proficiency_level_id": "invalid-uuid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # foreign key violation (proficiency doesn't exist)
    ([0], [0], [], [], USER_ID_1, MEDIA_ROLE_ID_1, {"proficiency_level_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_update_user_role_error_cases(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data, user_indices, role_indices, proficiency_indices, user_role_indices, user_id, role_id, payload, expected_status):
    """Test UPDATE user role error cases (400, 404, and 422)"""
    await conditional_seed(user_indices, test_users_data, seed_users)
    await conditional_seed(role_indices, test_media_roles_data, seed_media_roles)
    await conditional_seed(proficiency_indices, test_proficiency_levels_data, seed_proficiency_levels)
    await conditional_seed(user_role_indices, test_user_roles_data, seed_user_roles)
    response = await async_client.patch(f"/users/{user_id}/roles/{role_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_update_user_role_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data):
    """Test valid user role update"""
    await seed_users([test_users_data[0], test_users_data[1]])
    await seed_media_roles([test_media_roles_data[0], test_media_roles_data[1]])
    await seed_proficiency_levels(test_proficiency_levels_data[:3])
    await seed_user_roles([test_user_roles_data[0]])

    response = await async_client.patch(f"/users/{USER_ID_1}/roles/{MEDIA_ROLE_ID_1}", json={
        "proficiency_level_id": PROFICIENCY_LEVEL_ID_2
    })
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["user_id"] == USER_ID_1
    assert response_json["media_role_id"] == MEDIA_ROLE_ID_1
    assert response_json["proficiency_level_id"] == PROFICIENCY_LEVEL_ID_2

# =============================
# DELETE USER ROLE
# =============================
@pytest.mark.parametrize("user_id, role_id, expected_status", [
    # user role not found
    (USER_ID_1, MEDIA_ROLE_ID_2, status.HTTP_404_NOT_FOUND),
    # invalid UUID format for user_id
    ("invalid-uuid-format", MEDIA_ROLE_ID_1, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid UUID format for role_id
    (USER_ID_1, "invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_user_role_error_cases(async_client, user_id, role_id, expected_status):
    """Test DELETE user role error cases (404 and 422)"""
    response = await async_client.delete(f"/users/{user_id}/roles/{role_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_user_role_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data):
    """Test successful user role deletion with verification"""
    await seed_users([test_users_data[0]])
    await seed_media_roles([test_media_roles_data[0]])
    await seed_proficiency_levels([test_proficiency_levels_data[0]])
    await seed_user_roles([test_user_roles_data[0]])

    response = await async_client.delete(f"/users/{USER_ID_1}/roles/{MEDIA_ROLE_ID_1}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["user_id"] == USER_ID_1
    assert response_json["media_role_id"] == MEDIA_ROLE_ID_1

    verify_response = await async_client.get(f"/users/{USER_ID_1}/roles/{MEDIA_ROLE_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND
