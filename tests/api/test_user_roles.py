import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, USER_ID_1, USER_ID_2, USER_ID_3, ROLE_ID_1, ROLE_ID_2, ROLE_ID_3,
    PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2
)

# =============================
# FIXTURES
# =============================
@pytest.fixture
def seed_for_user_roles_tests(seed_users, seed_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_roles_data, test_proficiency_levels_data, test_user_roles_data):
    seed_users(test_users_data[:2])
    seed_roles(test_roles_data[:2])
    seed_proficiency_levels(test_proficiency_levels_data[:2])
    seed_user_roles(test_user_roles_data[:3])

# =============================
# GET ROLES FOR USER
# =============================
@pytest.mark.parametrize("user_id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # User not found
    ("invalid-uuid-format", status.HTTP_400_BAD_REQUEST), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_roles_for_user_error_cases(async_client, user_id, expected_status):
    """Test GET roles for user error cases (400, 404)"""
    response = await async_client.get(f"/users/{user_id}/roles")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_roles_for_user_none_exist(async_client, seed_users, test_users_data):
    """Test GET roles for user when none exist returns empty list"""
    seed_users([test_users_data[2]])
    response = await async_client.get(f"/users/{USER_ID_3}/roles")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_roles_for_user_success(async_client, seed_for_user_roles_tests):
    """Test GET roles for user success case"""
    response = await async_client.get(f"/users/{USER_ID_1}/roles")
    assert_list_200(response, expected_length=2)
    response_json = response.json()

    # shape assertions
    assert all("id" in ur for ur in response_json)
    assert all("user_id" in ur for ur in response_json)
    assert all("role_id" in ur for ur in response_json)
    assert all("proficiency_level_id" in ur for ur in response_json)
    assert all("user_last_name" in ur for ur in response_json)
    assert all("role_name" in ur for ur in response_json)
    assert all("proficiency_level_rank" in ur for ur in response_json)

    # data assertions
    assert all(ur["user_id"] == USER_ID_1 for ur in response_json)
    assert {ur["role_id"] for ur in response_json} == {ROLE_ID_1, ROLE_ID_2}
    assert {ur["proficiency_level_id"] for ur in response_json} == {PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2}
    assert response_json[0]["user_last_name"] == "Smith"
    assert response_json[0]["role_name"] == "ProPresenter"
    assert response_json[0]["proficiency_level_rank"] == 3

# =============================
# GET USERS FOR ROLE
# =============================
@pytest.mark.parametrize("role_id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Role not found
    ("invalid-uuid-format", status.HTTP_400_BAD_REQUEST), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_users_for_role_error_cases(async_client, role_id, expected_status):
    """Test GET users for role error cases (400, 404)"""
    response = await async_client.get(f"/roles/{role_id}/users")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_users_for_role_none_exist(async_client, seed_roles, test_roles_data):
    """Test GET users for role when none exist returns empty list"""
    seed_roles([test_roles_data[0]])
    response = await async_client.get(f"/roles/{ROLE_ID_1}/users")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_users_for_role_success(async_client, seed_for_user_roles_tests):
    """Test GET users for role success case"""
    response = await async_client.get(f"/roles/{ROLE_ID_1}/users")
    assert_list_200(response, expected_length=2)
    response_json = response.json()

    # shape assertions
    assert all("id" in ur for ur in response_json)
    assert all("role_id" in ur for ur in response_json)
    assert all("user_id" in ur for ur in response_json)
    assert all("proficiency_level_id" in ur for ur in response_json)
    assert all("user_email" in ur for ur in response_json)
    assert all("role_is_active" in ur for ur in response_json)
    assert all("proficiency_level_rank" in ur for ur in response_json)

    # data assertions
    assert all(ur["role_id"] == ROLE_ID_1 for ur in response_json)
    assert {ur["user_id"] for ur in response_json} == {USER_ID_1, USER_ID_2}
    assert all(ur["proficiency_level_id"] == PROFICIENCY_LEVEL_ID_1 for ur in response_json)
    assert response_json[0]["user_email"] == "alice@example.com"
    assert response_json[0]["role_is_active"] is True
    assert response_json[0]["proficiency_level_rank"] == 3

# # =============================
# # UPDATE USER ROLE
# # =============================
# @pytest.mark.parametrize("user_indices, role_indices, proficiency_indices, user_role_indices, user_id, role_id, payload, expected_status", [
#     # user role not found
#     ([], [], [], [], USER_ID_1, MEDIA_ROLE_ID_2, {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format for user_id
#     ([], [], [], [], "invalid-uuid-format", MEDIA_ROLE_ID_1, {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid UUID format for role_id
#     ([], [], [], [], USER_ID_1, "invalid-uuid-format", {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     ([], [], [], [], USER_ID_1, MEDIA_ROLE_ID_1, {}, status.HTTP_400_BAD_REQUEST),
#     # invalid UUID format in payload
#     ([], [], [], [], USER_ID_1, MEDIA_ROLE_ID_1, {"proficiency_level_id": "invalid-uuid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # foreign key violation (proficiency doesn't exist)
#     ([0], [0], [], [], USER_ID_1, MEDIA_ROLE_ID_1, {"proficiency_level_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_update_user_role_error_cases(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data, user_indices, role_indices, proficiency_indices, user_role_indices, user_id, role_id, payload, expected_status):
#     """Test UPDATE user role error cases (400, 404, and 422)"""
#     await conditional_seed(user_indices, test_users_data, seed_users)
#     await conditional_seed(role_indices, test_media_roles_data, seed_media_roles)
#     await conditional_seed(proficiency_indices, test_proficiency_levels_data, seed_proficiency_levels)
#     await conditional_seed(user_role_indices, test_user_roles_data, seed_user_roles)
#     response = await async_client.patch(f"/users/{user_id}/roles/{role_id}", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_update_user_role_success(async_client, seed_users, seed_media_roles, seed_proficiency_levels, seed_user_roles, test_users_data, test_media_roles_data, test_proficiency_levels_data, test_user_roles_data):
#     """Test valid user role update"""
#     await seed_users([test_users_data[0], test_users_data[1]])
#     await seed_media_roles([test_media_roles_data[0], test_media_roles_data[1]])
#     await seed_proficiency_levels(test_proficiency_levels_data[:3])
#     await seed_user_roles([test_user_roles_data[0]])

#     response = await async_client.patch(f"/users/{USER_ID_1}/roles/{MEDIA_ROLE_ID_1}", json={
#         "proficiency_level_id": PROFICIENCY_LEVEL_ID_2
#     })
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert response_json["user_id"] == USER_ID_1
#     assert response_json["media_role_id"] == MEDIA_ROLE_ID_1
#     assert response_json["proficiency_level_id"] == PROFICIENCY_LEVEL_ID_2