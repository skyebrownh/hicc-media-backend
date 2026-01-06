import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200
from tests.api.conftest import conditional_seed
from app.db.models import TeamUser
from sqlmodel import select
from tests.utils.constants import BAD_ID_0000, TEAM_ID_1, TEAM_ID_2, USER_ID_1, USER_ID_2, USER_ID_3

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
@pytest.mark.asyncio
async def test_get_users_for_team_error_cases(async_client, team_id, expected_status):
    """Test GET team users for team error cases (404 and 422)"""
    response = await async_client.get(f"/teams/{team_id}/users")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_users_for_team_none_exist(async_client, seed_teams, test_teams_data):
    """Test GET team users for team when none exist returns empty list"""
    seed_teams([test_teams_data[0]])
    response = await async_client.get(f"/teams/{TEAM_ID_1}/users")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_users_for_team_success(async_client, seed_for_team_users_tests):
    """Test GET team users for team success case"""
    response = await async_client.get(f"/teams/{TEAM_ID_1}/users")
    assert_list_200(response, expected_length=2)
    response_json = response.json()

    # shape assertions
    assert all("id" in tu for tu in response_json)
    assert all("team_id" in tu for tu in response_json)
    assert all("user_id" in tu for tu in response_json)
    assert all("team_code" in tu for tu in response_json)
    assert all("user_first_name" in tu for tu in response_json)
    
    # data assertions
    assert all(tu["team_id"] == TEAM_ID_1 for tu in response_json)
    assert {tu["user_id"] for tu in response_json} == {USER_ID_1, USER_ID_2}
    assert response_json[0]["team_code"] == "team_1"
    assert response_json[0]["user_first_name"] == "Alice"

# # =============================
# # INSERT TEAM USER
# # =============================
# @pytest.mark.parametrize("team_indices, user_indices, team_user_indices, payload, expected_status", [
#     # empty payload
#     ([], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields (user_id)
#     ([], [], [], {"team_id": TEAM_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields (team_id)
#     ([], [], [], {"user_id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid UUID format
#     ([], [], [], {"team_id": "invalid-uuid", "user_id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # duplicate team_user
#     ([0], [0], [0], {"team_id": TEAM_ID_1, "user_id": USER_ID_1}, status.HTTP_409_CONFLICT),
#     # extra fields not allowed
#     ([], [], [], {"team_id": TEAM_ID_1, "user_id": USER_ID_2, "team_user_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # foreign key violation (team doesn't exist)
#     ([], [1], [], {"team_id": BAD_ID_0000, "user_id": USER_ID_2}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_insert_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_indices, user_indices, team_user_indices, payload, expected_status):
#     """Test INSERT team user error cases (422, 409, and 404)"""
#     await conditional_seed(team_indices, test_teams_data, seed_teams)
#     await conditional_seed(user_indices, test_users_data, seed_users)
#     await conditional_seed(team_user_indices, test_team_users_data, seed_team_users)
#     response = await async_client.post("/team_users", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_insert_team_user_success(async_client, seed_teams, seed_users, test_teams_data, test_users_data):
#     """Test valid team user insertion"""
#     await seed_teams([test_teams_data[1]])
#     await seed_users([test_users_data[0]])
    
#     response = await async_client.post("/team_users", json={
#         "team_id": TEAM_ID_2,
#         "user_id": USER_ID_1
#     })
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert response_json["team_user_id"] is not None
#     assert response_json["team_id"] == TEAM_ID_2
#     assert response_json["user_id"] == USER_ID_1
#     assert response_json["is_active"] is True

# # =============================
# # UPDATE TEAM USER
# # =============================
# @pytest.mark.parametrize("team_indices, user_indices, team_user_indices, team_id, user_id, payload, expected_status", [
#     # team user not found
#     ([0], [1], [], TEAM_ID_1, USER_ID_2, {"is_active": False}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format for team_id
#     ([], [], [], "invalid-uuid-format", USER_ID_1, {"is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid UUID format for user_id
#     ([], [], [], TEAM_ID_1, "invalid-uuid-format", {"is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     ([], [], [], TEAM_ID_1, USER_ID_1, {}, status.HTTP_400_BAD_REQUEST),
#     # invalid data types
#     ([], [], [], TEAM_ID_1, USER_ID_1, {"is_active": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_update_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_indices, user_indices, team_user_indices, team_id, user_id, payload, expected_status):
#     """Test UPDATE team user error cases (400, 404, and 422)"""
#     await conditional_seed(team_indices, test_teams_data, seed_teams)
#     await conditional_seed(user_indices, test_users_data, seed_users)
#     await conditional_seed(team_user_indices, test_team_users_data, seed_team_users)
#     response = await async_client.patch(f"/teams/{team_id}/users/{user_id}", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.parametrize("team_id, user_id, payload, expected_fields", [
#     # update is_active to False
#     (
#         TEAM_ID_1,
#         USER_ID_1,
#         {"is_active": False},
#         {"is_active": False}
#     ),
#     # update is_active back to True
#     (
#         TEAM_ID_1,
#         USER_ID_1,
#         {"is_active": True},
#         {"is_active": True}
#     ),
# ])
# @pytest.mark.asyncio
# async def test_update_team_user_success(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_id, user_id, payload, expected_fields):
#     """Test valid team user updates"""
#     await seed_teams([test_teams_data[0]])
#     await seed_users([test_users_data[0]])
#     await seed_team_users([test_team_users_data[0]])
    
#     response = await async_client.patch(f"/teams/{team_id}/users/{user_id}", json=payload)
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert response_json["team_id"] == team_id
#     assert response_json["user_id"] == user_id
#     for field, expected_value in expected_fields.items():
#         assert response_json[field] == expected_value

# =============================
# DELETE TEAM USER
# =============================
@pytest.mark.asyncio
async def test_delete_team_user_error_cases(async_client, seed_teams, seed_users, test_teams_data, test_users_data):
    """Test DELETE team user error cases (422)"""
    seed_teams([test_teams_data[0]])
    seed_users([test_users_data[0]])
    response1 = await async_client.delete(f"/teams/invalid-uuid-format/users/{USER_ID_1}")
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    response2 = await async_client.delete(f"/teams/{TEAM_ID_1}/users/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_delete_team_user_success(async_client, get_test_db_session, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data):
    """Test successful team user deletion with verification"""
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

    # Verify valid team user that does not exist returns 204
    verify_response2 = await async_client.delete(f"/teams/{TEAM_ID_1}/users/{BAD_ID_0000}")
    assert verify_response2.status_code == status.HTTP_204_NO_CONTENT
    verify_response3 = await async_client.delete(f"/teams/{BAD_ID_0000}/users/{USER_ID_1}")
    assert verify_response3.status_code == status.HTTP_204_NO_CONTENT