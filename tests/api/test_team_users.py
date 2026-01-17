import pytest
from fastapi import status
from sqlmodel import select

from app.db.models import TeamUser
from tests.utils.helpers import assert_empty_list_200, assert_list_response, assert_single_item_response, conditional_seed, assert_keys_match
from tests.utils.constants import BAD_ID_0000, TEAM_ID_1, TEAM_ID_2, USER_ID_1, USER_ID_2

pytestmark = pytest.mark.asyncio

TEAM_USERS_RESPONSE_KEYS = {"id", "team_id", "user_id", "team_name", "team_code", "team_is_active", "user_first_name", "user_last_name", "user_email", "user_phone", "user_is_active", "is_active"}

# =============================
# FIXTURES
# =============================
@pytest.fixture
def seed_for_team_users_tests(seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data):
    seed_teams([test_teams_data[0]])
    seed_users(test_users_data[:2])
    seed_team_users(test_team_users_data[:2])

# =============================
# GET USERS FOR TEAM
# =============================
@pytest.mark.parametrize("team_id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Team not found
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_users_for_team_error_cases(async_client, team_id, expected_status):
    response = await async_client.get(f"/teams/{team_id}/users")
    assert response.status_code == expected_status

async def test_get_users_for_team_none_exist(async_client, seed_teams, test_teams_data):
    seed_teams([test_teams_data[0]])
    response = await async_client.get(f"/teams/{TEAM_ID_1}/users")
    assert_empty_list_200(response)

async def test_get_users_for_team_success(async_client, seed_for_team_users_tests):
    response = await async_client.get(f"/teams/{TEAM_ID_1}/users")
    assert_list_response(response, expected_length=2)
    response_json = response.json()
    response_dict = {tu["user_id"]: tu for tu in response_json}
    assert_keys_match(response_dict[USER_ID_1], TEAM_USERS_RESPONSE_KEYS)
    assert all(tu["team_id"] == TEAM_ID_1 for tu in response_json)
    assert {tu["user_id"] for tu in response_json} == {USER_ID_1, USER_ID_2}
    team_users_dict = {tu["user_id"]: tu for tu in response_json}
    assert team_users_dict[USER_ID_1]["team_code"] == "team_1"
    assert team_users_dict[USER_ID_1]["user_first_name"] == "Alice"

# =============================
# INSERT TEAM USER
# =============================
@pytest.mark.parametrize("team_id, user_indices, team_user_indices, payload, expected_status", [
    (BAD_ID_0000, [], [], {"user_id": USER_ID_1}, status.HTTP_404_NOT_FOUND), # team not found
    (TEAM_ID_1, [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT), # empty payload
    (TEAM_ID_1, [], [], {"is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields (user_id)
    (TEAM_ID_1, [], [], {"user_id": "invalid-uuid-format"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format in payload
    (TEAM_ID_1, [0], [0], {"user_id": USER_ID_1}, status.HTTP_409_CONFLICT), # duplicate team_user
    (TEAM_ID_1, [], [], {"user_id": USER_ID_2, "team_user_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT), # extra fields not allowed
])
async def test_insert_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_id, user_indices, team_user_indices, payload, expected_status):
    seed_teams([test_teams_data[0]])
    conditional_seed(user_indices, test_users_data, seed_users)
    conditional_seed(team_user_indices, test_team_users_data, seed_team_users)
    response = await async_client.post(f"/teams/{team_id}/users", json=payload)
    assert response.status_code == expected_status

async def test_insert_team_user_success(async_client, seed_teams, seed_users, test_teams_data, test_users_data):
    seed_teams([test_teams_data[1]])
    seed_users([test_users_data[0]])
    response = await async_client.post(f"/teams/{TEAM_ID_2}/users", json={"user_id": USER_ID_1})
    assert_single_item_response(response, expected_item={"team_id": TEAM_ID_2, "user_id": USER_ID_1, "is_active": True}, status_code=status.HTTP_201_CREATED)

# =============================
# UPDATE TEAM USER
# =============================
@pytest.mark.parametrize("team_id, user_id, payload, expected_status", [
    (BAD_ID_0000, USER_ID_1, {"is_active": False}, status.HTTP_404_NOT_FOUND), # team user not found (team not found)
    (TEAM_ID_1, BAD_ID_0000, {"is_active": False}, status.HTTP_404_NOT_FOUND), # team user not found (user not found)
    (TEAM_ID_1, "invalid-uuid-format", {"is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (TEAM_ID_1, USER_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (TEAM_ID_1, USER_ID_1, {"is_active": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (TEAM_ID_1, USER_ID_1, {"is_active": False, "id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT), # extra fields not allowed
])
async def test_update_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_id, user_id, payload, expected_status):
    seed_teams([test_teams_data[0]])
    seed_users([test_users_data[0]])
    seed_team_users([test_team_users_data[0]])
    response = await async_client.patch(f"/teams/{team_id}/users/{user_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    ({"is_active": False}, {}), # full update
])
async def test_update_team_user_success(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, payload, unchanged_fields):
    seed_teams([test_teams_data[0]])
    seed_users([test_users_data[0]])
    seed_team_users([test_team_users_data[0]])
    response = await async_client.patch(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == value

# =============================
# DELETE TEAM USER
# =============================
@pytest.mark.parametrize("team_id, user_id, expected_status", [
    ("invalid-uuid-format", USER_ID_1, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (BAD_ID_0000, USER_ID_1, status.HTTP_404_NOT_FOUND), # team not found
    (TEAM_ID_1, "invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (TEAM_ID_1, BAD_ID_0000, status.HTTP_404_NOT_FOUND), # user not found
])
async def test_delete_team_user_error_cases(async_client, seed_teams, seed_users, test_teams_data, test_users_data, team_id, user_id, expected_status):
    seed_teams([test_teams_data[0]])
    seed_users([test_users_data[0]])
    response = await async_client.delete(f"/teams/{team_id}/users/{user_id}")
    assert response.status_code == expected_status

async def test_delete_team_user_success(async_client, get_test_db_session, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data):
    seed_teams([test_teams_data[0]])
    seed_users([test_users_data[0]])
    seed_team_users([test_team_users_data[0]])
    response = await async_client.delete(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deletion by trying to query it directly
    verify_response = get_test_db_session.exec(
        select(TeamUser)
        .where(TeamUser.team_id == TEAM_ID_1)
        .where(TeamUser.user_id == USER_ID_1)
    ).first()
    assert verify_response is None