import pytest
from fastapi import status
from sqlmodel import select, func

from app.db.models import UserRole
from tests.utils.helpers import (
    assert_empty_list_200, assert_list_response, assert_single_item_response, conditional_seed,
    _filter_excluded_keys
)
from tests.utils.constants import BAD_ID_0000, PROFICIENCY_LEVEL_ID_3, ROLE_ID_1, ROLE_ID_2, ROLE_ID_3, USER_ID_1, USER_ID_2

pytestmark = pytest.mark.asyncio

ROLES_RESPONSE_KEYS = {"id", "name", "code", "order", "description", "is_active"}
VALID_UPDATE_PAYLOAD = {"name": "Updated Role Name", "description": "Updated description", "order": 100, "is_active": False}

# =============================
# GET ALL ROLES
# =============================
async def test_get_all_roles_none_exist(async_client):
    response = await async_client.get("/roles")
    assert_empty_list_200(response)

async def test_get_all_roles_success(async_client, seed_roles, test_roles_data):
    seed_roles(test_roles_data[:3])
    response = await async_client.get("/roles")
    assert_list_response(response, expected_length=3)
    response_json = response.json()
    response_dict = {r["id"]: r for r in response_json}
    assert set(_filter_excluded_keys(response_dict[ROLE_ID_1].keys())) == ROLES_RESPONSE_KEYS
    assert response_dict[ROLE_ID_1]["name"] == "ProPresenter"
    assert response_dict[ROLE_ID_2]["id"] is not None
    assert response_dict[ROLE_ID_2]["code"] == "sound"
    assert response_dict[ROLE_ID_2]["order"] == 20
    assert response_dict[ROLE_ID_3]["description"] is None
    assert response_dict[ROLE_ID_3]["is_active"] is True

# =============================
# GET SINGLE ROLE
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Role not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_single_role_error_cases(async_client, id, expected_status):
    response = await async_client.get(f"/roles/{id}")
    assert response.status_code == expected_status

async def test_get_single_role_success(async_client, seed_roles, test_roles_data):
    seed_roles([test_roles_data[0]])
    response = await async_client.get(f"/roles/{ROLE_ID_1}")
    assert_single_item_response(response, expected_item={
        "id": ROLE_ID_1,
        "name": "ProPresenter",
        "code": "propresenter",
        "order": 10,
        "description": None,
        "is_active": True
    })

# =============================
# INSERT ROLE
# =============================
@pytest.mark.parametrize("role_indices, payload, expected_status", [    
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT), # empty payload
    ([], {"name": "Incomplete Role"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    ([], {"name": "Bad Role", "order": "not_an_int", "code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([2], {"name": "Duplicate Code", "order": 6, "code": "new_role"}, status.HTTP_409_CONFLICT), # duplicate role_code
    ([], {"id": ROLE_ID_3, "name": "ID Not Allowed", "order": 7, "code": "id_not_allowed"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # role.id not allowed in payload
])
async def test_insert_role_error_cases(async_client, seed_roles, test_roles_data, role_indices, payload, expected_status):
    conditional_seed(role_indices, test_roles_data, seed_roles)
    response = await async_client.post("/roles", json=payload)
    assert response.status_code == expected_status

async def test_insert_role_success(async_client, get_test_db_session, seed_users, seed_proficiency_levels, test_users_data, test_proficiency_levels_data):
    seed_proficiency_levels([test_proficiency_levels_data[2]]) # Untrained proficiency level
    seed_users(test_users_data[:2])
    response = await async_client.post("/roles", json={"name": "New Role", "order": 4, "code": "new_role"})
    assert_single_item_response(response, expected_item={"name": "New Role", "code": "new_role", "order": 4, "description": None, "is_active": True}, status_code=status.HTTP_201_CREATED)

    # Verify user_roles were created for this new role
    role_id = response.json()["id"]
    user_roles = get_test_db_session.exec(select(UserRole).where(UserRole.role_id == role_id)).all()
    assert len(user_roles) == 2
    user_roles_dict = {str(ur.user_id): ur for ur in user_roles}
    assert str(user_roles_dict[USER_ID_1].user_id) == USER_ID_1
    assert str(user_roles_dict[USER_ID_1].proficiency_level_id) == PROFICIENCY_LEVEL_ID_3
    assert str(user_roles_dict[USER_ID_2].user_id) == USER_ID_2
    assert str(user_roles_dict[USER_ID_2].role_id) == role_id

# =============================
# UPDATE ROLE
# =============================
@pytest.mark.parametrize("role_id, payload, expected_status", [
    (BAD_ID_0000, VALID_UPDATE_PAYLOAD, status.HTTP_404_NOT_FOUND), # role not found
    ("invalid-uuid-format", VALID_UPDATE_PAYLOAD, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (ROLE_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (ROLE_ID_1, {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (ROLE_ID_1, {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
async def test_update_role_error_cases(async_client, seed_roles, test_roles_data, role_id, payload, expected_status):
    seed_roles([test_roles_data[0]])
    response = await async_client.patch(f"/roles/{role_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    (VALID_UPDATE_PAYLOAD, {"code": "propresenter"}), # full update
    ({"is_active": False}, {"name": "ProPresenter", "code": "propresenter"}), # partial update (is_active only)
    ({"name": "Partially Updated Role"}, {"code": "propresenter", "is_active": True}), # partial update (role_name only)
])
async def test_update_role_success(async_client, seed_roles, test_roles_data, payload, unchanged_fields):
    seed_roles([test_roles_data[0]])
    response = await async_client.patch(f"/roles/{ROLE_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == value

# =============================
# DELETE ROLE
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Role not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_delete_role_error_cases(async_client, id, expected_status):
    response = await async_client.delete(f"/roles/{id}")
    assert response.status_code == expected_status

async def test_delete_role_success(async_client, seed_roles, test_roles_data):
    seed_roles([test_roles_data[0]])
    response = await async_client.delete(f"/roles/{ROLE_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/roles/{ROLE_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

# =============================
# DELETE ROLE CASCADE
# =============================
@pytest.mark.parametrize("user_indices, proficiency_level_indices, user_role_indices, expected_count_before", [
    ([], [], [], 0), # No user_roles to cascade delete
    ([0], [0], [0], 1), # One user_role to cascade delete
    ([0, 1], [0], [0, 2], 2), # Multiple user_roles to cascade delete
])
async def test_delete_role_cascade_user_roles(
    async_client, get_test_db_session, seed_roles, seed_users, seed_proficiency_levels, seed_user_roles,
    test_roles_data, test_users_data, test_proficiency_levels_data, test_user_roles_data,
    user_indices, proficiency_level_indices, user_role_indices, expected_count_before
):
    # Seed parent
    seed_roles([test_roles_data[0]])

    # Seed child records based on parameters
    conditional_seed(user_indices, test_users_data, seed_users)
    conditional_seed(proficiency_level_indices, test_proficiency_levels_data, seed_proficiency_levels)
    conditional_seed(user_role_indices, test_user_roles_data, seed_user_roles)

    # Verify user_roles exist before deletion
    count_before = get_test_db_session.exec(select(func.count()).select_from(UserRole).where(UserRole.role_id == ROLE_ID_1)).one()
    assert count_before == expected_count_before

    # Delete parent
    response = await async_client.delete(f"/roles/{ROLE_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify parent is deleted
    verify_response = await async_client.get(f"/roles/{ROLE_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify all child records are cascade deleted
    count_after = get_test_db_session.exec(select(func.count()).select_from(UserRole).where(UserRole.role_id == ROLE_ID_1)).one()
    assert count_after == 0