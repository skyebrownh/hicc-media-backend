import pytest
from fastapi import status

pytestmark = pytest.mark.asyncio

from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, assert_single_item_201, conditional_seed
from tests.utils.constants import BAD_ID_0000, PROFICIENCY_LEVEL_ID_1, PROFICIENCY_LEVEL_ID_2, PROFICIENCY_LEVEL_ID_3

VALID_UPDATE_PAYLOAD = {
    "name": "Updated Level Name", 
    "rank": 100, 
    "is_active": False, 
    "is_assignable": True
}

# =============================
# GET ALL PROFICIENCY LEVELS
# =============================
async def test_get_all_proficiency_levels_none_exist(async_client):
    response = await async_client.get("/proficiency_levels")
    assert_empty_list_200(response)

async def test_get_all_proficiency_levels_success(async_client, seed_proficiency_levels, test_proficiency_levels_data):
    seed_proficiency_levels(test_proficiency_levels_data[:3])
    response = await async_client.get("/proficiency_levels")
    assert_list_200(response, expected_length=3)
    response_json = response.json()
    response_dict = {pl["id"]: pl for pl in response_json}
    assert response_dict[PROFICIENCY_LEVEL_ID_1]["name"] == "Novice"
    assert response_dict[PROFICIENCY_LEVEL_ID_2]["id"] is not None
    assert response_dict[PROFICIENCY_LEVEL_ID_2]["code"] == "proficient"
    assert response_dict[PROFICIENCY_LEVEL_ID_2]["rank"] == 4
    assert response_dict[PROFICIENCY_LEVEL_ID_3]["is_active"] is True
    assert response_dict[PROFICIENCY_LEVEL_ID_3]["is_assignable"] is True

# =============================
# GET SINGLE PROFICIENCY LEVEL
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Proficiency level not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_single_proficiency_level_error_cases(async_client, id, expected_status):
    response = await async_client.get(f"/proficiency_levels/{id}")
    assert response.status_code == expected_status

async def test_get_single_proficiency_level_success(async_client, seed_proficiency_levels, test_proficiency_levels_data):
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
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT), # empty payload
    ([], {"name": "Incomplete Proficiency Level"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    ([], {"name": "Bad Proficiency Level", "rank": "not_an_int", "code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([0], {"name": "Duplicate Code", "rank": 6, "code": "novice"}, status.HTTP_409_CONFLICT), # duplicate proficiency_level_code
    ([], {"id": BAD_ID_0000, "name": "ID Not Allowed", "rank": 7, "code": "id_not_allowed"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # proficiency_level_id not allowed in payload
])
async def test_insert_proficiency_level_error_cases(async_client, seed_proficiency_levels, test_proficiency_levels_data, proficiency_level_indices, payload, expected_status):
    conditional_seed(proficiency_level_indices, test_proficiency_levels_data, seed_proficiency_levels)
    response = await async_client.post("/proficiency_levels", json=payload)
    assert response.status_code == expected_status

async def test_insert_proficiency_level_success(async_client):
    response = await async_client.post("/proficiency_levels", json={"name": "New Level", "code": "new_level"})
    assert_single_item_201(response, expected_item={"name": "New Level", "code": "new_level", "rank": None, "is_active": True, "is_assignable": False})

# =============================
# UPDATE PROFICIENCY LEVEL
# =============================
@pytest.mark.parametrize("proficiency_level_id, payload, expected_status", [
    (BAD_ID_0000, VALID_UPDATE_PAYLOAD, status.HTTP_404_NOT_FOUND), # proficiency level not found
    ("invalid-uuid-format", VALID_UPDATE_PAYLOAD, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (PROFICIENCY_LEVEL_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (PROFICIENCY_LEVEL_ID_1, {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (PROFICIENCY_LEVEL_ID_1, {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
async def test_update_proficiency_level_error_cases(async_client, seed_proficiency_levels, test_proficiency_levels_data, proficiency_level_id, payload, expected_status):
    seed_proficiency_levels([test_proficiency_levels_data[0]])
    response = await async_client.patch(f"/proficiency_levels/{proficiency_level_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    (VALID_UPDATE_PAYLOAD, {"code": "novice"}), # full update
    ({"is_active": False}, {"name": "Novice", "code": "novice"}), # partial update (is_active only)
    ({"name": "Partially Updated Level"}, {"code": "novice", "is_active": True}), # partial update (level_name only)
])
async def test_update_proficiency_level_success(async_client, seed_proficiency_levels, test_proficiency_levels_data, payload, unchanged_fields):
    seed_proficiency_levels([test_proficiency_levels_data[0]])
    response = await async_client.patch(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == value

# =============================
# DELETE PROFICIENCY LEVEL
# =============================
async def test_delete_proficiency_level_error_cases(async_client):
    response = await async_client.delete("/proficiency_levels/invalid-uuid-format")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_delete_proficiency_level_success(async_client, seed_proficiency_levels, test_proficiency_levels_data):
    seed_proficiency_levels([test_proficiency_levels_data[0]])
    response = await async_client.delete(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/proficiency_levels/{PROFICIENCY_LEVEL_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND
