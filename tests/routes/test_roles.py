import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed, count_records
from tests.utils.constants import (
    BAD_ID_0000, ROLE_ID_1, ROLE_ID_2, ROLE_ID_3, ROLE_ID_4,
    USER_ID_1, USER_ID_2, PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2
)

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
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["name"] == "ProPresenter"
    assert response_json[1]["id"] is not None
    assert response_json[1]["code"] == "sound"
    assert response_json[1]["order"] == 20
    assert response_json[2]["description"] is None
    assert response_json[2]["is_active"] is True

# # =============================
# # GET SINGLE ROLE
# # =============================
# @pytest.mark.parametrize("role_id, expected_status", [
#     # Role not present
#     (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
#     # Invalid UUID format
#     ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_get_single_role_error_cases(async_client, role_id, expected_status):
#     """Test GET single role error cases (404 and 422)"""
#     response = await async_client.get(f"/roles/{role_id}")
#     assert response.status_code == expected_status


# @pytest.mark.asyncio
# async def test_get_single_role_success(async_client, seed_roles, test_roles_data):
#     """Test GET single role success case"""
#     await seed_roles([test_roles_data[1]])
    
#     response = await async_client.get(f"/roles/{role_ID_2}")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, dict)
#     assert response_json["name"] == "Sound"
#     assert response_json["code"] == "sound"
#     assert response_json["description"] is None
#     assert response_json["is_active"] is True

# # =============================
# # INSERT ROLE
# # =============================
# @pytest.mark.parametrize("role_indices, payload, expected_status", [
#     # empty payload
#     ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields
#    ([], {"name": "Incomplete Role"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid data types
#     ([], {"name": "Bad Role", "order": "not_an_int", "code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # duplicate role_code
#     ([3], {"name": "Duplicate Code", "order": 6, "code": "new_role"}, status.HTTP_409_CONFLICT),
#     # role_id not allowed in payload
#     ([4], {"id": role_ID_4, "name": "Duplicate ID Role", "order": 7, "code": "duplicate_id_role"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_insert_role_error_cases(async_client, seed_roles, test_roles_data, role_indices, payload, expected_status):
#     """Test INSERT role error cases (422 and 409)"""
#     await conditional_seed(role_indices, test_roles_data, seed_roles)
    
#     response = await async_client.post("/roles", json=payload)
#     assert response.status_code == expected_status


# @pytest.mark.asyncio
# async def test_insert_role_success(async_client):
#     """Test valid role insertion"""
#     response = await async_client.post("/roles", json={
#         "name": "New Role",
#         "order": 4,
#         "code": "new_role"
#     })
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert response_json["id"] is not None
#     assert response_json["name"] == "New Role"
#     assert response_json["code"] == "new_role"
#     assert response_json["is_active"] is True

# # =============================
# # UPDATE ROLE
# # =============================
# @pytest.mark.parametrize("role_indices, role_path, payload, expected_status", [
#     # role not found
#     ([], f"/roles/{BAD_ID_0000}", {"name": "Updated Role Name", "description": "Updated description", "order": 100, "is_active": False}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ([0], "/roles/invalid-uuid-format", {"name": "Updated Role Name", "description": "Updated description", "order": 100, "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     ([2], f"/roles/{role_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
#     # invalid data types
#     ([2], f"/roles/{role_ID_3}", {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # non-updatable field
#     ([2], f"/roles/{role_ID_3}", {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_update_role_error_cases(async_client, seed_roles, test_roles_data, role_indices, role_path, payload, expected_status):
#     """Test UPDATE role error cases (400, 404, and 422)"""
#     await conditional_seed(role_indices, test_roles_data, seed_roles)
    
#     response = await async_client.patch(role_path, json=payload)
#     assert response.status_code == expected_status


# @pytest.mark.parametrize("role_id, payload, expected_fields, unchanged_fields", [
#     # full update
#     (
#         role_ID_3,
#         {"name": "Updated Role Name", "description": "Updated description", "order": 100, "is_active": False},
#         {"name": "Updated Role Name", "description": "Updated description", "is_active": False},
#         {"code": "lighting"}
#     ),
#     # partial update (is_active only)
#     (
#         role_ID_2,
#         {"is_active": False},
#         {"is_active": False},
#         {"name": "Sound", "code": "sound"}
#     ),
#     # partial update (role_name only)
#     (
#         role_ID_1,
#         {"name": "Partially Updated Role"},
#         {"name": "Partially Updated Role"},
#         {"code": "propresenter", "is_active": True}
#     ),
# ])
# @pytest.mark.asyncio
# async def test_update_role_success(async_client, seed_roles, test_roles_data, role_id, payload, expected_fields, unchanged_fields):
#     """Test valid role updates"""
#     await seed_roles(test_roles_data[:3])
    
#     response = await async_client.patch(f"/roles/{role_id}", json=payload)
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     for field, expected_value in expected_fields.items():
#         assert response_json[field] == expected_value
#     for field, expected_value in unchanged_fields.items():
#         assert response_json[field] == expected_value

# # =============================
# # DELETE ROLE
# # =============================
# @pytest.mark.parametrize("role_indices, role_path, expected_status", [
#     # role not found
#     ([], f"/roles/{BAD_ID_0000}", status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ([0], "/roles/invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_delete_role_error_cases(async_client, seed_roles, test_roles_data, role_indices, role_path, expected_status):
#     """Test DELETE role error cases (404 and 422)"""
#     await conditional_seed(role_indices, test_roles_data, seed_roles)
    
#     response = await async_client.delete(role_path)
#     assert response.status_code == expected_status


# @pytest.mark.asyncio
# async def test_delete_role_success(async_client, seed_roles, test_roles_data):
#     """Test successful role deletion with verification"""
#     await seed_roles([test_roles_data[1]])

#     # Test successful deletion
#     response = await async_client.delete(f"/roles/{role_ID_2}")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, dict)
#     assert response_json["id"] == role_ID_2

#     # Verify deletion by trying to get it again
#     verify_response = await async_client.get(f"/roles/{role_ID_2}")
#     assert verify_response.status_code == status.HTTP_404_NOT_FOUND

# # =============================
# # DELETE ROLE CASCADE
# # =============================
# @pytest.mark.parametrize("user_indices, proficiency_level_indices, user_role_indices, expected_count_before", [
#     # No user_roles to cascade delete
#     ([], [], [], 0),
#     # One user_role to cascade delete
#     ([0], [0], [0], 1),
#     # Multiple user_roles to cascade delete
#     ([0, 1], [0, 1], [0, 1], 2),
# ])
# @pytest.mark.asyncio
# async def test_delete_role_cascade_user_roles(
#     async_client, test_db_pool, seed_roles, seed_users, seed_proficiency_levels, seed_user_roles,
#     test_roles_data, test_users_data, test_proficiency_levels_data, test_user_roles_data,
#     user_indices, proficiency_level_indices, user_role_indices, expected_count_before
# ):
#     """Test that deleting a role cascades to delete associated user_roles"""
#     # Seed parent
#     await seed_roles([test_roles_data[0]])

#     # Seed child records based on parameters
#     await conditional_seed(user_indices, test_users_data[:2], seed_users)
#     await conditional_seed(proficiency_level_indices, test_proficiency_levels_data[:2], seed_proficiency_levels)
#     user_roles_for_cascade = [
#         {"user_id": USER_ID_1, "id": role_ID_1, "proficiency_level_id": PROFICIENCY_LEVEL_ID_1},
#         {"user_id": USER_ID_2, "id": role_ID_1, "proficiency_level_id": PROFICIENCY_LEVEL_ID_2},
#     ]
#     await conditional_seed(user_role_indices, user_roles_for_cascade, seed_user_roles)

#     # Verify user_roles exist before deletion
#     count_before = await count_records(test_db_pool, "user_roles", f"id = '{role_ID_1}'")
#     assert count_before == expected_count_before

#     # Delete parent
#     response = await async_client.delete(f"/roles/{role_ID_1}")
#     assert response.status_code == status.HTTP_200_OK

#     # Verify parent is deleted
#     verify_response = await async_client.get(f"/roles/{role_ID_1}")
#     assert verify_response.status_code == status.HTTP_404_NOT_FOUND

#     # Verify all child records are cascade deleted
#     count_after = await count_records(test_db_pool, "user_roles", f"id = '{role_ID_1}'")
#     assert count_after == 0