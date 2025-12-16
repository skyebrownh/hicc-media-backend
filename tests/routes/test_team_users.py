import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.utils.constants import (
    BAD_ID_0000, TEAM_ID_1, TEAM_ID_2, USER_ID_1, USER_ID_2, USER_ID_3
)

# =============================
# DATA FIXTURES
# =============================
@pytest.fixture
def test_teams_data():
    """Fixture providing array of test team data"""
    return [
        {"team_id": TEAM_ID_1, "team_name": "Team 1", "team_code": "team_1"},
        {"team_id": TEAM_ID_2, "team_name": "Team 2", "team_code": "team_2"},
    ]

@pytest.fixture
def test_users_data():
    """Fixture providing array of test user data"""
    return [
        {"user_id": USER_ID_1, "first_name": "John", "last_name": "Doe", "phone": "555-0101"},
        {"user_id": USER_ID_2, "first_name": "Jane", "last_name": "Smith", "phone": "555-0102"},
        {"user_id": USER_ID_3, "first_name": "Bob", "last_name": "Johnson", "phone": "555-0103"},
    ]

@pytest.fixture
def test_team_users_data():
    """Fixture providing array of test team_user data"""
    return [
        {"team_id": TEAM_ID_1, "user_id": USER_ID_1},
        {"team_id": TEAM_ID_1, "user_id": USER_ID_2},
        {"team_id": TEAM_ID_2, "user_id": USER_ID_3},
    ]

# =============================
# GET ALL TEAM USERS
# =============================
@pytest.mark.asyncio
async def test_get_all_team_users_none_exist(async_client):
    """Test when no team users exist returns empty list"""
    response = await async_client.get("/team_users")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_team_users_success(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data):
    """Test getting all team users after inserting a variety"""
    await seed_teams(test_teams_data)
    await seed_users(test_users_data)
    await seed_team_users(test_team_users_data)

    response = await async_client.get("/team_users")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["team_user_id"] is not None
    assert response_json[0]["team_id"] == TEAM_ID_1
    assert response_json[1]["user_id"] == USER_ID_2
    assert response_json[2]["is_active"] is True
    assert response_json[2]["user_id"] == USER_ID_3

# =============================
# GET TEAM USERS FOR TEAM
# =============================
@pytest.mark.parametrize("team_id, expected_status", [
    # Team not found
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_team_users_for_team_error_cases(async_client, team_id, expected_status):
    """Test GET team users for team error cases (404 and 422)"""
    response = await async_client.get(f"/teams/{team_id}/users")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_team_users_for_team_none_exist(async_client, seed_teams, seed_users, test_teams_data, test_users_data):
    """Test GET team users for team when none exist returns empty list"""
    await seed_teams(test_teams_data)
    await seed_users([test_users_data[0]])

    response = await async_client.get(f"/teams/{TEAM_ID_2}/users")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_team_users_for_team_success(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data):
    """Test GET team users for team success case"""
    await seed_teams(test_teams_data)
    await seed_users(test_users_data[:2])
    await seed_team_users(test_team_users_data[:2])

    response = await async_client.get(f"/teams/{TEAM_ID_1}/users")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2
    assert all(tu["team_id"] == TEAM_ID_1 for tu in response_json)
    assert {tu["user_id"] for tu in response_json} == {USER_ID_1, USER_ID_2}

# =============================
# GET SINGLE TEAM USER
# =============================
@pytest.mark.parametrize("team_indices, user_indices, team_user_indices, team_id, user_id, expected_status", [
    # Team user not found
    ([0], [], [], TEAM_ID_1, BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format for team_id
    ([], [], [], "invalid-uuid-format", USER_ID_1, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # Invalid UUID format for user_id
    ([], [], [], TEAM_ID_1, "invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_indices, user_indices, team_user_indices, team_id, user_id, expected_status):
    """Test GET single team user error cases (404 and 422)"""
    teams = [test_teams_data[i] for i in team_indices]
    users = [test_users_data[i] for i in user_indices]
    team_users = [test_team_users_data[i] for i in team_user_indices]
    await seed_teams(teams)
    await seed_users(users)
    await seed_team_users(team_users)
    response = await async_client.get(f"/teams/{team_id}/users/{user_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_team_user_success(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data):
    """Test GET single team user success case"""
    await seed_teams([test_teams_data[0]])
    await seed_users([test_users_data[0]])
    await seed_team_users([test_team_users_data[0]])

    response = await async_client.get(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["team_id"] == TEAM_ID_1
    assert response_json["user_id"] == USER_ID_1
    assert response_json["is_active"] is True
    assert response_json["team_user_id"] is not None

# =============================
# INSERT TEAM USER
# =============================
@pytest.mark.parametrize("team_indices, user_indices, team_user_indices, payload, expected_status", [
    # empty payload
    ([], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields (user_id)
    ([], [], [], {"team_id": TEAM_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields (team_id)
    ([], [], [], {"user_id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid UUID format
    ([], [], [], {"team_id": "invalid-uuid", "user_id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # duplicate team_user
    ([0], [0], [0], {"team_id": TEAM_ID_1, "user_id": USER_ID_1}, status.HTTP_409_CONFLICT),
    # extra fields not allowed
    ([], [], [], {"team_id": TEAM_ID_1, "user_id": USER_ID_2, "team_user_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # foreign key violation (team doesn't exist)
    ([], [1], [], {"team_id": BAD_ID_0000, "user_id": USER_ID_2}, status.HTTP_404_NOT_FOUND),
])
@pytest.mark.asyncio
async def test_insert_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_indices, user_indices, team_user_indices, payload, expected_status):
    """Test INSERT team user error cases (422, 409, and 404)"""
    teams = [test_teams_data[i] for i in team_indices]
    users = [test_users_data[i] for i in user_indices]
    team_users = [test_team_users_data[i] for i in team_user_indices]
    await seed_teams(teams)
    await seed_users(users)
    await seed_team_users(team_users)
    response = await async_client.post("/team_users", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_team_user_success(async_client, seed_teams, seed_users, test_teams_data, test_users_data):
    """Test valid team user insertion"""
    await seed_teams([test_teams_data[1]])
    await seed_users([test_users_data[0]])
    
    response = await async_client.post("/team_users", json={
        "team_id": TEAM_ID_2,
        "user_id": USER_ID_1
    })
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["team_user_id"] is not None
    assert response_json["team_id"] == TEAM_ID_2
    assert response_json["user_id"] == USER_ID_1
    assert response_json["is_active"] is True

# =============================
# UPDATE TEAM USER
# =============================
@pytest.mark.parametrize("team_indices, user_indices, team_user_indices, team_id, user_id, payload, expected_status", [
    # team user not found
    ([0], [1], [], TEAM_ID_1, USER_ID_2, {"is_active": False}, status.HTTP_404_NOT_FOUND),
    # invalid UUID format for team_id
    ([], [], [], "invalid-uuid-format", USER_ID_1, {"is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid UUID format for user_id
    ([], [], [], TEAM_ID_1, "invalid-uuid-format", {"is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    ([], [], [], TEAM_ID_1, USER_ID_1, {}, status.HTTP_400_BAD_REQUEST),
    # invalid data types
    ([], [], [], TEAM_ID_1, USER_ID_1, {"is_active": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_update_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_indices, user_indices, team_user_indices, team_id, user_id, payload, expected_status):
    """Test UPDATE team user error cases (400, 404, and 422)"""
    teams = [test_teams_data[i] for i in team_indices]
    users = [test_users_data[i] for i in user_indices]
    team_users = [test_team_users_data[i] for i in team_user_indices]
    await seed_teams(teams)
    await seed_users(users)
    await seed_team_users(team_users)
    response = await async_client.patch(f"/teams/{team_id}/users/{user_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("team_id, user_id, payload, expected_fields", [
    # update is_active to False
    (
        TEAM_ID_1,
        USER_ID_1,
        {"is_active": False},
        {"is_active": False}
    ),
    # update is_active back to True
    (
        TEAM_ID_1,
        USER_ID_1,
        {"is_active": True},
        {"is_active": True}
    ),
])
@pytest.mark.asyncio
async def test_update_team_user_success(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_id, user_id, payload, expected_fields):
    """Test valid team user updates"""
    await seed_teams([test_teams_data[0]])
    await seed_users([test_users_data[0]])
    await seed_team_users([test_team_users_data[0]])
    
    response = await async_client.patch(f"/teams/{team_id}/users/{user_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["team_id"] == team_id
    assert response_json["user_id"] == user_id
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE TEAM USER
# =============================
@pytest.mark.parametrize("team_indices, user_indices, team_user_indices, team_id, user_id, expected_status", [
    # team user not found
    ([0], [1], [], TEAM_ID_1, USER_ID_2, status.HTTP_404_NOT_FOUND),
    # invalid UUID format for team_id
    ([], [], [], "invalid-uuid-format", USER_ID_1, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid UUID format for user_id
    ([], [], [], TEAM_ID_1, "invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_team_user_error_cases(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data, team_indices, user_indices, team_user_indices, team_id, user_id, expected_status):
    """Test DELETE team user error cases (404 and 422)"""
    teams = [test_teams_data[i] for i in team_indices]
    users = [test_users_data[i] for i in user_indices]
    team_users = [test_team_users_data[i] for i in team_user_indices]
    await seed_teams(teams)
    await seed_users(users)
    await seed_team_users(team_users)
    response = await async_client.delete(f"/teams/{team_id}/users/{user_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_team_user_success(async_client, seed_teams, seed_users, seed_team_users, test_teams_data, test_users_data, test_team_users_data):
    """Test successful team user deletion with verification"""
    await seed_teams([test_teams_data[0]])
    await seed_users([test_users_data[0]])
    await seed_team_users([test_team_users_data[0]])

    response = await async_client.delete(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["team_id"] == TEAM_ID_1
    assert response_json["user_id"] == USER_ID_1
    assert response_json["is_active"] is True

    verify_response = await async_client.get(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND
