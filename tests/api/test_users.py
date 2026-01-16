import pytest
from fastapi import status
from sqlmodel import select, func

from app.db.models import TeamUser, UserRole
from tests.utils.helpers import (
    assert_empty_list_200, assert_list_200, assert_single_item_200, assert_single_item_201, conditional_seed,
    _filter_timestamp_keys
)
from tests.utils.constants import BAD_ID_0000, ROLE_ID_1, ROLE_ID_2, USER_ID_1, USER_ID_2, USER_ID_3, PROFICIENCY_LEVEL_ID_3

pytestmark = pytest.mark.asyncio

USERS_RESPONSE_KEYS = {"id", "first_name", "last_name", "email", "phone", "is_active"}

VALID_UPDATE_PAYLOAD = {
    "first_name": "Updated First Name",
    "last_name": "Updated Last Name",
    "email": "updated@example.com",
    "phone": "555-7777",
    "is_active": False
}

# =============================
# GET ALL USERS
# =============================
async def test_get_all_users_none_exist(async_client):
    response = await async_client.get("/users")
    assert_empty_list_200(response)

async def test_get_all_users_success(async_client, seed_users, test_users_data):
    seed_users(test_users_data[:3])
    response = await async_client.get("/users")
    assert_list_200(response, expected_length=3)
    response_json = response.json()
    response_dict = {u["id"]: u for u in response_json}
    assert set(_filter_timestamp_keys(response_dict[USER_ID_1].keys())) == USERS_RESPONSE_KEYS
    assert response_dict[USER_ID_1]["first_name"] == "Alice"
    assert response_dict[USER_ID_2]["id"] is not None
    assert response_dict[USER_ID_2]["email"] == "bob@example.com"
    assert response_dict[USER_ID_3]["phone"] == "555-3333"
    assert response_dict[USER_ID_3]["is_active"] is True

# =============================
# GET SINGLE USER
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # User not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_single_user_error_cases(async_client, id, expected_status):
    response = await async_client.get(f"/users/{id}")
    assert response.status_code == expected_status

async def test_get_single_user_success(async_client, seed_users, test_users_data):
    seed_users([test_users_data[0]])
    response = await async_client.get(f"/users/{USER_ID_1}")
    assert_single_item_200(response, expected_item={
        "id": USER_ID_1,
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone": "555-1111",
        "is_active": True
    })

# =============================
# INSERT USER
# =============================
@pytest.mark.parametrize("payload, expected_status", [
    ({}, status.HTTP_422_UNPROCESSABLE_CONTENT), # empty payload
    ({ "first_name": "Incomplete"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    ({ "first_name": 123, "last_name": True, "phone": 555, "email": 999}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ({ "id": BAD_ID_0000, "first_name": "ID Not Allowed", "last_name": "ID", "phone": "555-6666", "email": "id_not_allowed@example.com"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # user_id not allowed in payload
])
async def test_insert_user_error_cases(async_client, payload, expected_status):
    response = await async_client.post("/users", json=payload)
    assert response.status_code == expected_status

async def test_insert_user_success(async_client, get_test_db_session, seed_roles, seed_proficiency_levels, test_roles_data, test_proficiency_levels_data):
    seed_proficiency_levels([test_proficiency_levels_data[2]]) # Untrained proficiency level
    seed_roles(test_roles_data[:2])
    response = await async_client.post("/users", json={"first_name": "New", "last_name": "User", "phone": "555-4444", "email": "newuser@example.com"})
    assert_single_item_201(response, expected_item={"first_name": "New", "last_name": "User", "phone": "555-4444", "email": "newuser@example.com", "is_active": True})

    # Verify user_roles were created for this new user
    user_id = response.json()["id"]
    user_roles = get_test_db_session.exec(select(UserRole).where(UserRole.user_id == user_id)).all()
    assert len(user_roles) == 2
    user_roles_dict = {str(ur.role_id): ur for ur in user_roles}
    assert str(user_roles_dict[ROLE_ID_1].role_id) == ROLE_ID_1
    assert str(user_roles_dict[ROLE_ID_1].proficiency_level_id) == PROFICIENCY_LEVEL_ID_3
    assert str(user_roles_dict[ROLE_ID_2].role_id) == ROLE_ID_2
    assert str(user_roles_dict[ROLE_ID_2].user_id) == user_id

# =============================
# UPDATE USER
# =============================
@pytest.mark.parametrize("user_id, payload, expected_status", [
    (BAD_ID_0000, VALID_UPDATE_PAYLOAD, status.HTTP_404_NOT_FOUND), # user not found
    ("invalid-uuid-format", VALID_UPDATE_PAYLOAD, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (USER_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (USER_ID_1, {"first_name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (USER_ID_1, {"first_name": "Invalid", "id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
async def test_update_user_error_cases(async_client, seed_users, test_users_data, user_id, payload, expected_status):
    seed_users([test_users_data[0]])
    response = await async_client.patch(f"/users/{user_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    (VALID_UPDATE_PAYLOAD, {}), # full update
    ({"is_active": False}, {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "phone": "555-1111"}), # partial update (is_active only)
    ({"first_name": "Partially Updated User"}, {"last_name": "Smith", "email": "alice@example.com", "phone": "555-1111", "is_active": True}), # partial update (first_name only)
])
async def test_update_user_success(async_client, seed_users, test_users_data, payload, unchanged_fields):
    seed_users([test_users_data[0]])
    response = await async_client.patch(f"/users/{USER_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == value

# =============================
# DELETE USER
# =============================
async def test_delete_user_error_cases(async_client):
    response = await async_client.delete("/users/invalid-uuid-format")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_delete_user_success(async_client, seed_users, test_users_data):
    seed_users([test_users_data[0]])
    response = await async_client.delete(f"/users/{USER_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/users/{USER_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

# =============================
# DELETE USER CASCADE
# =============================
@pytest.mark.parametrize("team_indices, team_user_indices, role_indices, user_role_indices, expected_team_user_count, expected_user_role_count", [
    ([], [], [], [], 0, 0), # No children to cascade delete
    ([0], [0], [], [], 1, 0), # One team_user, no user_roles
    ([], [], [0], [0], 0, 1), # No team_users, one user_role
    ([0, 1], [0, 2], [], [], 2, 0), # Multiple team_users, no user_roles
    ([], [], [0, 1], [0, 1], 0, 2), # Multiple user_roles, no team_users
    ([0, 1], [0, 2], [0, 1], [0, 1], 2, 2), # Multiple team_users, multiple user_roles
])
async def test_delete_user_cascade(
    async_client, get_test_db_session, seed_users, seed_teams, seed_team_users, seed_roles, seed_proficiency_levels, seed_user_roles,
    test_users_data, test_teams_data, test_team_users_data, test_roles_data, test_proficiency_levels_data, test_user_roles_data,
    team_indices, team_user_indices, role_indices, user_role_indices,
    expected_team_user_count, expected_user_role_count
):
    # Seed parent
    seed_users([test_users_data[0]])

    # Seed child records based on parameters
    seed_proficiency_levels(test_proficiency_levels_data[:2])
    conditional_seed(team_indices, test_teams_data, seed_teams)
    conditional_seed(team_user_indices, test_team_users_data, seed_team_users)
    conditional_seed(role_indices, test_roles_data, seed_roles)
    conditional_seed(user_role_indices, test_user_roles_data, seed_user_roles)

    # Verify children exist before deletion
    team_user_count_before = get_test_db_session.exec(select(func.count()).select_from(TeamUser).where(TeamUser.user_id == USER_ID_1)).one()
    user_role_count_before = get_test_db_session.exec(select(func.count()).select_from(UserRole).where(UserRole.user_id == USER_ID_1)).one()
    assert team_user_count_before == expected_team_user_count
    assert user_role_count_before == expected_user_role_count

    # Delete parent
    response = await async_client.delete(f"/users/{USER_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify parent is deleted
    verify_response = await async_client.get(f"/users/{USER_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify all child records are cascade deleted
    team_user_count_after = get_test_db_session.exec(select(func.count()).select_from(TeamUser).where(TeamUser.user_id == USER_ID_1)).one()
    user_role_count_after = get_test_db_session.exec(select(func.count()).select_from(UserRole).where(UserRole.user_id == USER_ID_1)).one()
    assert team_user_count_after == 0
    assert user_role_count_after == 0