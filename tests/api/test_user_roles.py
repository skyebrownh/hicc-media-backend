import pytest
from fastapi import status

from tests.utils.helpers import assert_empty_list_200, assert_list_response
from tests.utils.constants import BAD_ID_0000, USER_ID_1, USER_ID_2, USER_ID_3, ROLE_ID_1, ROLE_ID_2, PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2

pytestmark = pytest.mark.asyncio

USER_ROLES_RESPONSE_KEYS = {"id", "user_id", "role_id", "proficiency_level_id", "user_first_name", "user_last_name", "user_email", "user_phone", "user_is_active", "role_name", "role_description", "role_order", "role_is_active", "role_code", "proficiency_level_name", "proficiency_level_rank", "proficiency_level_is_assignable", "proficiency_level_is_active", "proficiency_level_code"}

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
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_roles_for_user_error_cases(async_client, user_id, expected_status):
    response = await async_client.get(f"/users/{user_id}/roles")
    assert response.status_code == expected_status

async def test_get_roles_for_user_none_exist(async_client, seed_users, test_users_data):
    seed_users([test_users_data[2]])
    response = await async_client.get(f"/users/{USER_ID_3}/roles")
    assert_empty_list_200(response)

async def test_get_roles_for_user_success(async_client, seed_for_user_roles_tests):
    response = await async_client.get(f"/users/{USER_ID_1}/roles")
    assert_list_response(response, expected_length=2)
    response_json = response.json()
    response_dict = {ur["role_id"]: ur for ur in response_json}
    assert set(response_dict[ROLE_ID_1].keys()) == USER_ROLES_RESPONSE_KEYS
    assert all(ur["user_id"] == USER_ID_1 for ur in response_json)
    assert {ur["role_id"] for ur in response_json} == {ROLE_ID_1, ROLE_ID_2}
    assert {ur["proficiency_level_id"] for ur in response_json} == {PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2}
    user_roles_dict = {ur["role_id"]: ur for ur in response_json}
    assert user_roles_dict[ROLE_ID_1]["user_last_name"] == "Smith"
    assert user_roles_dict[ROLE_ID_1]["role_name"] == "ProPresenter"
    assert user_roles_dict[ROLE_ID_1]["proficiency_level_rank"] == 3

# =============================
# GET USERS FOR ROLE
# =============================
@pytest.mark.parametrize("role_id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Role not found
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_users_for_role_error_cases(async_client, role_id, expected_status):
    response = await async_client.get(f"/roles/{role_id}/users")
    assert response.status_code == expected_status

async def test_get_users_for_role_none_exist(async_client, seed_roles, test_roles_data):
    seed_roles([test_roles_data[0]])
    response = await async_client.get(f"/roles/{ROLE_ID_1}/users")
    assert_empty_list_200(response)

async def test_get_users_for_role_success(async_client, seed_for_user_roles_tests):
    response = await async_client.get(f"/roles/{ROLE_ID_1}/users")
    assert_list_response(response, expected_length=2)
    response_json = response.json()
    response_dict = {ur["user_id"]: ur for ur in response_json}
    assert set(response_dict[USER_ID_1].keys()) == USER_ROLES_RESPONSE_KEYS
    assert all(ur["role_id"] == ROLE_ID_1 for ur in response_json)
    assert {ur["user_id"] for ur in response_json} == {USER_ID_1, USER_ID_2}
    assert all(ur["proficiency_level_id"] == PROFICIENCY_LEVEL_ID_1 for ur in response_json)
    user_roles_dict = {ur["user_id"]: ur for ur in response_json}
    assert user_roles_dict[USER_ID_1]["user_email"] == "alice@example.com"
    assert user_roles_dict[USER_ID_1]["role_is_active"] is True
    assert user_roles_dict[USER_ID_1]["proficiency_level_rank"] == 3

# =============================
# UPDATE USER ROLE
# =============================
@pytest.mark.parametrize("user_id, role_id, payload, expected_status", [
    (BAD_ID_0000, ROLE_ID_1, {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_404_NOT_FOUND), # user role not found (user not found)
    (USER_ID_1, BAD_ID_0000, {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_404_NOT_FOUND), # user role not found (role not found)
    (USER_ID_1, "invalid-uuid-format", {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (USER_ID_1, ROLE_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (USER_ID_1, ROLE_ID_1, {"proficiency_level_id": BAD_ID_0000}, status.HTTP_409_CONFLICT), # FK violation
    (USER_ID_1, ROLE_ID_1, {"proficiency_level_id": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (USER_ID_1, ROLE_ID_1, {"proficiency_level_id": PROFICIENCY_LEVEL_ID_2, "id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT), # extra fields not allowed
])
async def test_update_user_role_error_cases(async_client, seed_proficiency_levels, seed_users, seed_roles, seed_user_roles, test_proficiency_levels_data, test_users_data, test_roles_data, test_user_roles_data, user_id, role_id, payload, expected_status):
    seed_proficiency_levels(test_proficiency_levels_data[:2])
    seed_users([test_users_data[0]])
    seed_roles([test_roles_data[0]])
    seed_user_roles([test_user_roles_data[0]])
    response = await async_client.patch(f"/users/{user_id}/roles/{role_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    ({"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, {}), # full update
    # ({"proficiency_level_id": PROFICIENCY_LEVEL_ID_2}, {}), # partial update (proficiency_level_id only)
])
async def test_update_user_role_success(async_client, seed_proficiency_levels, seed_users, seed_roles, seed_user_roles, test_proficiency_levels_data, test_users_data, test_roles_data, test_user_roles_data, payload, unchanged_fields):
    seed_proficiency_levels(test_proficiency_levels_data[:2])
    seed_users([test_users_data[0]])
    seed_roles([test_roles_data[0]])
    seed_user_roles([test_user_roles_data[0]])
    response = await async_client.patch(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == value