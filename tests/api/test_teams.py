import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, assert_single_item_201, conditional_seed
from sqlmodel import select, func
from app.db.models import TeamUser
from tests.utils.constants import BAD_ID_0000, TEAM_ID_1, TEAM_ID_3

# =============================
# GET ALL TEAMS
# =============================
@pytest.mark.asyncio
async def test_get_all_teams_none_exist(async_client):
    """Test when no teams exist returns empty list"""
    response = await async_client.get("/teams")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_teams_success(async_client, seed_teams, test_teams_data):
    """Test getting all teams after inserting a variety"""
    seed_teams(test_teams_data[:3])
    response = await async_client.get("/teams")
    assert_list_200(response, expected_length=3)
    response_json = response.json()
    assert response_json[0]["name"] == "Team 1"
    assert response_json[1]["id"] is not None
    assert response_json[1]["code"] == "team_2"
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE TEAM
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Team not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_team_error_cases(async_client, id, expected_status):
    """Test GET single team error cases (404, 422)"""
    response = await async_client.get(f"/teams/{id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_team_success(async_client, seed_teams, test_teams_data):
    """Test GET single team success case"""
    seed_teams([test_teams_data[0]])
    response = await async_client.get(f"/teams/{TEAM_ID_1}")
    assert_single_item_200(response, expected_item={
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
@pytest.mark.asyncio
async def test_insert_team_error_cases(async_client, seed_teams, test_teams_data, team_indices, payload, expected_status):
    """Test INSERT team error cases (422, and 409)"""
    conditional_seed(team_indices, test_teams_data, seed_teams)
    response = await async_client.post("/teams", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_team_success(async_client):
    """Test valid team insertion"""
    response = await async_client.post("/teams", json={"name": "New Team", "code": "new_team"})
    assert_single_item_201(response, expected_item={"name": "New Team", "code": "new_team", "is_active": True})

# # =============================
# # UPDATE TEAM
# # =============================
@pytest.mark.parametrize("team_indices, team_id, payload, expected_status", [
    ([], BAD_ID_0000, {"name": "Updated Team Name", "is_active": False}, status.HTTP_404_NOT_FOUND), # team not found
    ([], "invalid-uuid-format", {"name": "Updated Team Name", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    ([0], TEAM_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    ([0], TEAM_ID_1, {"name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    ([0], TEAM_ID_1, {"name": "Invalid", "code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
@pytest.mark.asyncio
async def test_update_team_error_cases(async_client, seed_teams, test_teams_data, team_indices, team_id, payload, expected_status):
    """Test UPDATE team error cases (400, 404, and 422)"""
    conditional_seed(team_indices, test_teams_data, seed_teams)
    response = await async_client.patch(f"/teams/{team_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    ({"name": "Updated Team Name", "is_active": False}, {"code": "team_1"}), # full update
    ({"is_active": False}, {"name": "Service", "code": "service"}), # partial update (is_active only)
    ({"name": "Partially Updated Team"}, {"code": "team_1", "is_active": True}), # partial update (team_name only)
])
@pytest.mark.asyncio
async def test_update_team_success(async_client, seed_teams, test_teams_data, payload, unchanged_fields):
    """Test valid team updates"""
    seed_teams([test_teams_data[0]])
    response = await async_client.patch(f"/teams/{TEAM_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == getattr(test_teams_data[0], field)

# =============================
# DELETE TEAM
# =============================
@pytest.mark.asyncio
async def test_delete_team_error_cases(async_client):
    """Test DELETE team error cases (422)"""
    response = await async_client.delete("/teams/invalid-uuid-format")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_delete_team_success(async_client, seed_teams, test_teams_data):
    """Test successful team deletion with verification"""
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
@pytest.mark.asyncio
async def test_delete_team_cascade_team_users(
    async_client, get_test_db_session, seed_teams, seed_users, seed_team_users,
    test_teams_data, test_users_data, test_team_users_data,
    user_indices, team_user_indices, expected_count_before
):
    """Test that deleting a team cascades to delete associated team_users"""
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
