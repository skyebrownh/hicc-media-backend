import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, assert_single_item_201, conditional_seed
from sqlmodel import select, func
from app.db.models import UserRole
from tests.utils.constants import BAD_ID_0000, PROFICIENCY_LEVEL_ID_3, ROLE_ID_1, ROLE_ID_4, PROFICIENCY_LEVEL_ID_3, USER_ID_1, USER_ID_2

VALID_UPDATE_PAYLOAD = {
    "name": "Updated Role Name",
    "description": "Updated description",
    "order": 100,
    "is_active": False
}

# =============================
# GET ALL ROLES
# =============================
@pytest.mark.asyncio
async def test_get_all_roles_none_exist(async_client):
    """Test when no roles exist returns empty list"""
    response = await async_client.get("/roles")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_roles_success(async_client, seed_roles, test_roles_data):
    """Test getting all roles after inserting a variety"""
    seed_roles(test_roles_data[:3])
    response = await async_client.get("/roles")
    assert_list_200(response, expected_length=3)
    
    response_json = response.json()
    assert response_json[0]["name"] == "ProPresenter"
    assert response_json[1]["id"] is not None
    assert response_json[1]["code"] == "sound"
    assert response_json[1]["order"] == 20
    assert response_json[2]["description"] is None
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE ROLE
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Role not present
    ("invalid-uuid-format", status.HTTP_400_BAD_REQUEST), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_role_error_cases(async_client, id, expected_status):
    """Test GET single role error cases (400, 404)"""
    response = await async_client.get(f"/roles/{id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_role_success(async_client, seed_roles, test_roles_data):
    """Test GET single role success case"""
    seed_roles([test_roles_data[0]])
    response = await async_client.get(f"/roles/{ROLE_ID_1}")
    assert_single_item_200(response, expected_item={
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
    ([], {}, status.HTTP_400_BAD_REQUEST), # empty payload
    ([], {"name": "Incomplete Role"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    ([], {"name": "Bad Role", "order": "not_an_int", "code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([3], {"name": "Duplicate Code", "order": 6, "code": "new_role"}, status.HTTP_409_CONFLICT), # duplicate role_code
    ([], {"id": ROLE_ID_4, "name": "ID Not Allowed", "order": 7, "code": "id_not_allowed"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # role_id not allowed in payload
])
@pytest.mark.asyncio
async def test_insert_role_error_cases(async_client, seed_roles, test_roles_data, role_indices, payload, expected_status):
    """Test INSERT role error cases (400, 422, and 409)"""
    conditional_seed(role_indices, test_roles_data, seed_roles)
    response = await async_client.post("/roles", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_role_success(async_client, get_test_db_session, seed_users, seed_proficiency_levels, test_users_data, test_proficiency_levels_data):
    """Test valid role insertion"""
    seed_proficiency_levels([test_proficiency_levels_data[2]]) # Untrained proficiency level
    seed_users(test_users_data[:2])
    response = await async_client.post("/roles", json={"name": "New Role", "order": 4, "code": "new_role"})
    assert_single_item_201(response, expected_item={"name": "New Role", "code": "new_role", "order": 4, "description": None, "is_active": True})

    # Verify user_roles were created for this new role
    role_id = response.json()["id"]
    user_roles = get_test_db_session.exec(select(UserRole).where(UserRole.role_id == role_id)).all()
    assert len(user_roles) == 2
    assert str(user_roles[0].user_id) == USER_ID_1
    assert str(user_roles[0].proficiency_level_id) == PROFICIENCY_LEVEL_ID_3
    assert str(user_roles[1].user_id) == USER_ID_2
    assert str(user_roles[1].role_id) == role_id

# =============================
# UPDATE ROLE
# =============================
@pytest.mark.parametrize("role_indices, role_id, payload, expected_status", [
    ([], BAD_ID_0000, VALID_UPDATE_PAYLOAD, status.HTTP_404_NOT_FOUND), # role not found
    ([], "invalid-uuid-format", VALID_UPDATE_PAYLOAD, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    ([0], ROLE_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    ([0], ROLE_ID_1, {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([0], ROLE_ID_1, {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
@pytest.mark.asyncio
async def test_update_role_error_cases(async_client, seed_roles, test_roles_data, role_indices, role_id, payload, expected_status):
    """Test UPDATE role error cases (400, 404, and 422)"""
    conditional_seed(role_indices, test_roles_data, seed_roles)
    response = await async_client.patch(f"/roles/{role_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    (VALID_UPDATE_PAYLOAD, {"code": "propresenter"}), # full update
    ({"is_active": False}, {"name": "ProPresenter", "code": "propresenter"}), # partial update (is_active only)
    ({"name": "Partially Updated Role"}, {"code": "propresenter", "is_active": True}), # partial update (role_name only)
])
@pytest.mark.asyncio
async def test_update_role_success(async_client, seed_roles, test_roles_data, payload, unchanged_fields):
    """Test valid role updates"""
    seed_roles([test_roles_data[0]])
    response = await async_client.patch(f"/roles/{ROLE_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == getattr(test_roles_data[0], field)

# =============================
# DELETE ROLE
# =============================
@pytest.mark.asyncio
async def test_delete_role_error_cases(async_client):
    """Test DELETE role error cases (400)"""
    response = await async_client.delete("/roles/invalid-uuid-format")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_delete_role_success(async_client, seed_roles, test_roles_data):
    """Test successful role deletion with verification"""
    seed_roles([test_roles_data[0]])
    response = await async_client.delete(f"/roles/{ROLE_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/roles/{ROLE_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify valid role id that does not exist returns 204
    verify_response2 = await async_client.delete(f"/roles/{BAD_ID_0000}")
    assert verify_response2.status_code == status.HTTP_204_NO_CONTENT

# =============================
# DELETE ROLE CASCADE
# =============================
@pytest.mark.parametrize("user_indices, proficiency_level_indices, user_role_indices, expected_count_before", [
    ([], [], [], 0), # No user_roles to cascade delete
    ([0], [0], [0], 1), # One user_role to cascade delete
    ([0, 1], [0], [0, 2], 2), # Multiple user_roles to cascade delete
])
@pytest.mark.asyncio
async def test_delete_role_cascade_user_roles(
    async_client, get_test_db_session, seed_roles, seed_users, seed_proficiency_levels, seed_user_roles,
    test_roles_data, test_users_data, test_proficiency_levels_data, test_user_roles_data,
    user_indices, proficiency_level_indices, user_role_indices, expected_count_before
):
    """Test that deleting a role cascades to delete associated user_roles"""
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