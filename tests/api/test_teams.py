import pytest
from fastapi import status
from sqlmodel import select, func

from app.db.models import TeamUser
from tests.utils.helpers import (
    assert_empty_list_200, assert_list_response, assert_single_item_response, conditional_seed,
    _filter_excluded_keys
)
from tests.utils.constants import BAD_ID_0000, TEAM_ID_1, TEAM_ID_2, TEAM_ID_3

pytestmark = pytest.mark.asyncio

TEAMS_RESPONSE_KEYS = {"id", "name", "code", "is_active"}

# =============================
# GET ALL TEAMS
# =============================
async def test_get_all_teams_none_exist(async_client):
    response = await async_client.get("/teams")
    assert_empty_list_200(response)

async def test_get_all_teams_success(async_client, seed_teams, test_teams_data):
    seed_teams(test_teams_data[:3])
    response = await async_client.get("/teams")
    assert_list_response(response, expected_length=3)
    response_json = response.json()
    response_dict = {t["id"]: t for t in response_json}
    assert set(_filter_excluded_keys(response_dict[TEAM_ID_1].keys())) == TEAMS_RESPONSE_KEYS
    assert response_dict[TEAM_ID_1]["name"] == "Team 1"
    assert response_dict[TEAM_ID_2]["id"] is not None
    assert response_dict[TEAM_ID_2]["code"] == "team_2"
    assert response_dict[TEAM_ID_3]["is_active"] is True

# =============================
# GET SINGLE TEAM
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Team not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_single_team_error_cases(async_client, id, expected_status):
    response = await async_client.get(f"/teams/{id}")
    assert response.status_code == expected_status

async def test_get_single_team_success(async_client, seed_teams, test_teams_data):
    seed_teams([test_teams_data[0]])
    response = await async_client.get(f"/teams/{TEAM_ID_1}")
    assert_single_item_response(response, expected_item={
        "id": TEAM_ID_1,
        "name": "Team 1",
        "code": "team_1",
        "is_active": True
    })

# =============================
# INSERT TEAM
# =============================
@pytest.mark.parametrize("team_indices, payload, expected_status", [
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT), # empty payload
    ([], {"name": "Incomplete Team"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    ([], {"name": "Bad Team", "code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([2], {"name": "Duplicate Team Code", "code": "new_team"}, status.HTTP_409_CONFLICT), # duplicate team_code
    ([], {"id": TEAM_ID_3, "name": "ID Not Allowed", "code": "id_not_allowed"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # team_id not allowed in payload
])
async def test_insert_team_error_cases(async_client, seed_teams, test_teams_data, team_indices, payload, expected_status):
    conditional_seed(team_indices, test_teams_data, seed_teams)
    response = await async_client.post("/teams", json=payload)
    assert response.status_code == expected_status

async def test_insert_team_success(async_client):
    response = await async_client.post("/teams", json={"name": "New Team", "code": "new_team"})
    assert_single_item_response(response, expected_item={"name": "New Team", "code": "new_team", "is_active": True}, status_code=status.HTTP_201_CREATED)

# =============================
# UPDATE TEAM
# =============================
@pytest.mark.parametrize("team_id, payload, expected_status", [
    (BAD_ID_0000, {"name": "Updated Team Name", "is_active": False}, status.HTTP_404_NOT_FOUND), # team not found
    ("invalid-uuid-format", {"name": "Updated Team Name", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (TEAM_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (TEAM_ID_1, {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (TEAM_ID_1, {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
async def test_update_team_error_cases(async_client, seed_teams, test_teams_data, team_id, payload, expected_status):
    seed_teams([test_teams_data[0]])
    response = await async_client.patch(f"/teams/{team_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    ({"name": "Updated Team Name", "is_active": False}, {"code": "team_1"}), # full update
    ({"is_active": False}, {"name": "Team 1", "code": "team_1"}), # partial update (is_active only)
    ({"name": "Partially Updated Team"}, {"code": "team_1", "is_active": True}), # partial update (team_name only)
])
async def test_update_team_success(async_client, seed_teams, test_teams_data, payload, unchanged_fields):
    seed_teams([test_teams_data[0]])
    response = await async_client.patch(f"/teams/{TEAM_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == value

# =============================
# DELETE TEAM
# =============================
async def test_delete_team_error_cases(async_client):
    response = await async_client.delete("/teams/invalid-uuid-format")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_delete_team_success(async_client, seed_teams, test_teams_data):
    seed_teams([test_teams_data[0]])
    response = await async_client.delete(f"/teams/{TEAM_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/teams/{TEAM_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

# =============================
# DELETE TEAM CASCADE
# =============================
@pytest.mark.parametrize("user_indices, team_user_indices, expected_count_before", [
    ([], [], 0), # No team_users to cascade delete
    ([0], [0], 1), # One team_user to cascade delete
    ([0, 1], [0, 1], 2), # Multiple team_users to cascade delete
])
async def test_delete_team_cascade_team_users(
    async_client, get_test_db_session, seed_teams, seed_users, seed_team_users,
    test_teams_data, test_users_data, test_team_users_data,
    user_indices, team_user_indices, expected_count_before
):
    # Seed parent
    seed_teams([test_teams_data[0]])

    # Seed child records based on parameters
    conditional_seed(user_indices, test_users_data, seed_users)
    conditional_seed(team_user_indices, test_team_users_data, seed_team_users)

    # Verify team_users exist before deletion
    count_before = get_test_db_session.exec(select(func.count()).select_from(TeamUser).where(TeamUser.team_id == TEAM_ID_1)).one()
    assert count_before == expected_count_before

    # Delete parent
    response = await async_client.delete(f"/teams/{TEAM_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify parent is deleted
    verify_response = await async_client.get(f"/teams/{TEAM_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify all child records are cascade deleted
    count_after = get_test_db_session.exec(select(func.count()).select_from(TeamUser).where(TeamUser.team_id == TEAM_ID_1)).one()
    assert count_after == 0