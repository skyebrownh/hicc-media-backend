import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, assert_single_item_201, conditional_seed
from tests.utils.constants import BAD_ID_0000, PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2, PROFICIENCY_LEVEL_ID_3, PROFICIENCY_LEVEL_ID_4

# =============================
# GET ALL PROFICIENCY LEVELS
# =============================
@pytest.mark.asyncio
async def test_get_all_proficiency_levels_none_exist(async_client):
    """Test when no proficiency levels exist returns empty list"""
    response = await async_client.get("/proficiency_levels")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_proficiency_levels_success(async_client, seed_proficiency_levels, test_proficiency_levels_data):
    """Test getting all proficiency levels after inserting a variety"""
    seed_proficiency_levels(test_proficiency_levels_data[:3])
    response = await async_client.get("/proficiency_levels")
    assert_list_200(response, expected_length=3)
    response_json = response.json()
    assert response_json[0]["name"] == "Novice"
    assert response_json[1]["id"] is not None
    assert response_json[1]["code"] == "proficient"
    assert response_json[1]["rank"] == 4
    assert response_json[2]["is_active"] is True
    assert response_json[2]["is_assignable"] is True

# =============================
# GET SINGLE PROFICIENCY LEVEL
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Proficiency level not present
    ("invalid-uuid-format", status.HTTP_400_BAD_REQUEST), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_proficiency_level_error_cases(async_client, id, expected_status):
    """Test GET single proficiency level error cases (400, 404)"""
    response = await async_client.get(f"/proficiency_levels/{id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_proficiency_level_success(async_client, seed_proficiency_levels, test_proficiency_levels_data):
    """Test GET single proficiency level success case"""
    seed_proficiency_levels([test_proficiency_levels_data[0]])
    response = await async_client.get(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}")
    assert_single_item_200(response, expected_item={
        "id": PROFICIENCY_LEVEL_ID_1,
        "name": "Novice",
        "code": "novice",
        "rank": 3,
        "is_active": True,
        "is_assignable": True
    })

# =============================
# INSERT PROFICIENCY LEVEL
# =============================
@pytest.mark.parametrize("proficiency_level_indices, payload, expected_status", [
    ([], {}, status.HTTP_400_BAD_REQUEST), # empty payload
    ([], {"name": "Incomplete Proficiency Level"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    ([], {"name": "Bad Proficiency Level", "rank": "not_an_int", "code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([3], {"name": "Duplicate Code", "rank": 6, "code": "new_level"}, status.HTTP_409_CONFLICT), # duplicate proficiency_level_code
    ([], {"id": PROFICIENCY_LEVEL_ID_4, "name": "ID Not Allowed", "rank": 7, "code": "id_not_allowed"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # proficiency_level_id not allowed in payload
])
@pytest.mark.asyncio
async def test_insert_proficiency_level_error_cases(async_client, seed_proficiency_levels, test_proficiency_levels_data, proficiency_level_indices, payload, expected_status):
    """Test INSERT proficiency level error cases (400, 422, and 409)"""
    conditional_seed(proficiency_level_indices, test_proficiency_levels_data, seed_proficiency_levels)
    response = await async_client.post("/proficiency_levels", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_proficiency_level_success(async_client):
    """Test valid proficiency level insertion"""
    response = await async_client.post("/proficiency_levels", json={"name": "New Level", "code": "new_level"})
    assert_single_item_201(response, expected_item={"name": "New Level", "code": "new_level", "rank": None, "is_active": True, "is_assignable": False})

# # =============================
# # UPDATE PROFICIENCY LEVEL
# # =============================
# @pytest.mark.parametrize("level_indices, url_path, payload, expected_status", [
#     # proficiency level not found
#     ([], f"/proficiency_levels/{BAD_ID_0000}", {"name": "Updated Level Name", "rank": 100, "is_active": False, "is_assignable": True}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ([0], "/proficiency_levels/invalid-uuid-format", {"name": "Updated Level Name", "rank": 100, "is_active": False, "is_assignable": True}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     ([2], f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
#     # invalid data types
#     ([2], f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # non-updatable field
#     ([2], f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_update_proficiency_level_error_cases(async_client, seed_proficiency_levels, test_proficiency_levels_data, level_indices, url_path, payload, expected_status):
#     """Test UPDATE proficiency level error cases (400, 404, and 422)"""
#     await conditional_seed(level_indices, test_proficiency_levels_data, seed_proficiency_levels)
    
#     response = await async_client.patch(url_path, json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.parametrize("proficiency_level_id, payload, expected_fields, unchanged_fields", [
#     # full update
#     (
#         PROFICIENCY_LEVEL_ID_3,
#         {"name": "Updated Level Name", "rank": 100, "is_active": False, "is_assignable": True},
#         {"name": "Updated Level Name", "rank": 100, "is_active": False, "is_assignable": True},
#         {"code": "untrained"}
#     ),
#     # partial update (is_active only)
#     (
#         PROFICIENCY_LEVEL_ID_2,
#         {"is_active": False},
#         {"is_active": False},
#         {"name": "Proficient", "code": "proficient"}
#     ),
#     # partial update (proficiency_level_name only)
#     (
#         PROFICIENCY_LEVEL_ID_1,
#         {"name": "Partially Updated Level"},
#         {"name": "Partially Updated Level"},
#         {"code": "novice", "is_active": True}
#     ),
# ])
# @pytest.mark.asyncio
# async def test_update_proficiency_level_success(async_client, seed_proficiency_levels, test_proficiency_levels_data, proficiency_level_id, payload, expected_fields, unchanged_fields):
#     """Test valid proficiency level updates"""
#     await seed_proficiency_levels(test_proficiency_levels_data[:3])
    
#     response = await async_client.patch(f"/proficiency_levels/{proficiency_level_id}", json=payload)
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     for field, expected_value in expected_fields.items():
#         assert response_json[field] == expected_value
#     for field, expected_value in unchanged_fields.items():
#         assert response_json[field] == expected_value

# =============================
# DELETE PROFICIENCY LEVEL
# =============================
@pytest.mark.asyncio
async def test_delete_proficiency_level_error_cases(async_client):
    """Test DELETE proficiency level error cases (400)"""
    response = await async_client.delete("/proficiency_levels/invalid-uuid-format")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_delete_proficiency_level_success(async_client, seed_proficiency_levels, test_proficiency_levels_data):
    """Test successful proficiency level deletion with verification"""
    seed_proficiency_levels([test_proficiency_levels_data[0]])
    response = await async_client.delete(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify valid proficiency level id that does not exist returns 204
    verify_response2 = await async_client.delete(f"/proficiency_levels/{BAD_ID_0000}")
    assert verify_response2.status_code == status.HTTP_204_NO_CONTENT
