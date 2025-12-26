import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200
from tests.routes.conftest import conditional_seed
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
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_proficiency_level_error_cases(async_client, id, expected_status):
    """Test GET single proficiency level error cases (404 and 422)"""
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

# # =============================
# # INSERT PROFICIENCY LEVEL
# # =============================
# @pytest.mark.parametrize("level_indices, payload, expected_status", [
#     # empty payload
#     ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields
#     ([], {"proficiency_level_name": "Incomplete Level"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid data types
#     ([], {"proficiency_level_name": "Bad Level", "proficiency_level_number": "not_an_int", "proficiency_level_code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # duplicate proficiency_level_code
#     ([3], {"proficiency_level_name": "Duplicate Code", "proficiency_level_number": 6, "proficiency_level_code": "new_level"}, status.HTTP_409_CONFLICT),
#     # proficiency_level_id not allowed in payload
#     ([4], {"proficiency_level_id": PROFICIENCY_LEVEL_ID_4, "proficiency_level_name": "Duplicate ID Level", "proficiency_level_number": 7, "proficiency_level_code": "duplicate_id_level"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_insert_proficiency_level_error_cases(async_client, seed_proficiency_levels, test_proficiency_levels_data, level_indices, payload, expected_status):
#     """Test INSERT proficiency level error cases (422 and 409)"""
#     await conditional_seed(level_indices, test_proficiency_levels_data, seed_proficiency_levels)
    
#     response = await async_client.post("/proficiency_levels", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_insert_proficiency_level_success(async_client):
#     """Test valid proficiency level insertion"""
#     response = await async_client.post("/proficiency_levels", json={
#         "proficiency_level_name": "New Level",
#         "proficiency_level_code": "new_level"
#     })
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert response_json["proficiency_level_id"] is not None
#     assert response_json["proficiency_level_name"] == "New Level"
#     assert response_json["proficiency_level_number"] is None
#     assert response_json["proficiency_level_code"] == "new_level"
#     assert response_json["is_active"] is True
#     assert response_json["is_assignable"] is False

# # =============================
# # UPDATE PROFICIENCY LEVEL
# # =============================
# @pytest.mark.parametrize("level_indices, proficiency_level_path, payload, expected_status", [
#     # proficiency level not found
#     ([], f"/proficiency_levels/{BAD_ID_0000}", {"proficiency_level_name": "Updated Level Name", "proficiency_level_number": 100, "is_active": False, "is_assignable": True}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ([0], "/proficiency_levels/invalid-uuid-format", {"proficiency_level_name": "Updated Level Name", "proficiency_level_number": 100, "is_active": False, "is_assignable": True}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     ([2], f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
#     # invalid data types
#     ([2], f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", {"proficiency_level_name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # non-updatable field
#     ([2], f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_3}", {"proficiency_level_name": "Invalid", "proficiency_level_code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_update_proficiency_level_error_cases(async_client, seed_proficiency_levels, test_proficiency_levels_data, level_indices, proficiency_level_path, payload, expected_status):
#     """Test UPDATE proficiency level error cases (400, 404, and 422)"""
#     await conditional_seed(level_indices, test_proficiency_levels_data, seed_proficiency_levels)
    
#     response = await async_client.patch(proficiency_level_path, json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.parametrize("proficiency_level_id, payload, expected_fields, unchanged_fields", [
#     # full update
#     (
#         PROFICIENCY_LEVEL_ID_3,
#         {"proficiency_level_name": "Updated Level Name", "proficiency_level_number": 100, "is_active": False, "is_assignable": True},
#         {"proficiency_level_name": "Updated Level Name", "proficiency_level_number": 100, "is_active": False, "is_assignable": True},
#         {"proficiency_level_code": "untrained"}
#     ),
#     # partial update (is_active only)
#     (
#         PROFICIENCY_LEVEL_ID_2,
#         {"is_active": False},
#         {"is_active": False},
#         {"proficiency_level_name": "Proficient", "proficiency_level_code": "proficient"}
#     ),
#     # partial update (proficiency_level_name only)
#     (
#         PROFICIENCY_LEVEL_ID_1,
#         {"proficiency_level_name": "Partially Updated Level"},
#         {"proficiency_level_name": "Partially Updated Level"},
#         {"proficiency_level_code": "novice", "is_active": True}
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

# # =============================
# # DELETE PROFICIENCY LEVEL
# # =============================
# @pytest.mark.parametrize("level_indices, proficiency_level_path, expected_status", [
#     # proficiency level not found
#     ([], f"/proficiency_levels/{BAD_ID_0000}", status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ([0], "/proficiency_levels/invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_delete_proficiency_level_error_cases(async_client, seed_proficiency_levels, test_proficiency_levels_data, level_indices, proficiency_level_path, expected_status):
#     """Test DELETE proficiency level error cases (404 and 422)"""
#     await conditional_seed(level_indices, test_proficiency_levels_data, seed_proficiency_levels)
    
#     response = await async_client.delete(proficiency_level_path)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_delete_proficiency_level_success(async_client, seed_proficiency_levels, test_proficiency_levels_data):
#     """Test successful proficiency level deletion with verification"""
#     await seed_proficiency_levels([test_proficiency_levels_data[1]])

#     # Test successful deletion
#     response = await async_client.delete(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_2}")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, dict)
#     assert response_json["proficiency_level_id"] == PROFICIENCY_LEVEL_ID_2

#     # Verify deletion by trying to get it again
#     verify_response = await async_client.get(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_2}")
#     assert verify_response.status_code == status.HTTP_404_NOT_FOUND
