import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import BAD_ID_0000, TEAM_ID_1, TEAM_ID_2, TEAM_ID_3, TEAM_ID_4

# =============================
# DATA FIXTURES
# =============================
@pytest.fixture
def test_teams_data():
    """Fixture providing array of test team data"""
    return [
        {"team_id": TEAM_ID_1, "team_name": "Team 1", "team_code": "team_1"},
        {"team_id": TEAM_ID_2, "team_name": "Team 2", "team_code": "team_2"},
        {"team_id": TEAM_ID_3, "team_name": "Team 3", "team_code": "team_3"},
        {"team_id": TEAM_ID_4, "team_name": "Another Team", "team_code": "new_team"},
    ]

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
    await seed_teams(test_teams_data[:3])

    response = await async_client.get("/teams")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["team_name"] == "Team 1"
    assert response_json[1]["team_id"] is not None
    assert response_json[1]["team_code"] == "team_2"
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE TEAM
# =============================
@pytest.mark.parametrize("team_id, expected_status", [
    # Team not present
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
    # Invalid UUID format
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_team_error_cases(async_client, team_id, expected_status):
    """Test GET single team error cases (404 and 422)"""
    response = await async_client.get(f"/teams/{team_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_team_success(async_client, seed_teams, test_teams_data):
    """Test GET single team success case"""
    await seed_teams([test_teams_data[0], test_teams_data[1]])
    
    response = await async_client.get(f"/teams/{TEAM_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["team_name"] == "Team 2"
    assert response_json["team_code"] == "team_2"
    assert response_json["is_active"] is True

# =============================
# INSERT TEAM
# =============================
@pytest.mark.parametrize("team_indices, payload, expected_status", [
    # empty payload
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields
    ([], {"team_name": "Incomplete Team"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid data types
    ([], {"team_name": "Bad Team", "team_code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # duplicate team_code
    ([3], {"team_name": "Duplicate Team Code", "team_code": "new_team"}, status.HTTP_409_CONFLICT),
    # team_id not allowed in payload
    ([3], {"team_id": TEAM_ID_4, "team_name": "Duplicate ID Team", "team_code": "duplicate_id_team"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_insert_team_error_cases(async_client, seed_teams, test_teams_data, team_indices, payload, expected_status):
    """Test INSERT team error cases (422 and 409)"""
    await conditional_seed(team_indices, test_teams_data, seed_teams)
    
    response = await async_client.post("/teams", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_team_success(async_client):
    """Test valid team insertion"""
    response = await async_client.post("/teams", json={"team_name": "New Team", "team_code": "new_team"})
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["team_id"] is not None
    assert response_json["team_name"] == "New Team"
    assert response_json["team_code"] == "new_team"
    assert response_json["is_active"] is True

# =============================
# UPDATE TEAM
# =============================
@pytest.mark.parametrize("team_indices, team_path, payload, expected_status", [
    # team not found
    ([], f"/teams/{BAD_ID_0000}", {"team_name": "Updated Team Name", "is_active": False}, status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ([0], "/teams/invalid-uuid-format", {"team_name": "Updated Team Name", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    ([2], f"/teams/{TEAM_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
    # invalid data types
    ([2], f"/teams/{TEAM_ID_3}", {"team_name": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # non-updatable field
    ([2], f"/teams/{TEAM_ID_3}", {"team_name": "Invalid", "team_code": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_update_team_error_cases(async_client, seed_teams, test_teams_data, team_indices, team_path, payload, expected_status):
    """Test UPDATE team error cases (400, 404, and 422)"""
    await conditional_seed(team_indices, test_teams_data, seed_teams)
    
    response = await async_client.patch(team_path, json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("team_id, payload, expected_fields, unchanged_fields", [
    # full update
    (
        TEAM_ID_3,
        {"team_name": "Updated Team Name", "is_active": False},
        {"team_name": "Updated Team Name", "is_active": False},
        {"team_code": "team_3"}
    ),
    # partial update (is_active only)
    (
        TEAM_ID_2,
        {"is_active": False},
        {"is_active": False},
        {"team_name": "Team 2", "team_code": "team_2"}
    ),
    # partial update (team_name only)
    (
        TEAM_ID_1,
        {"team_name": "Partially Updated Team"},
        {"team_name": "Partially Updated Team"},
        {"team_code": "team_1", "is_active": True}
    ),
])
@pytest.mark.asyncio
async def test_update_team_success(async_client, seed_teams, test_teams_data, team_id, payload, expected_fields, unchanged_fields):
    """Test valid team updates"""
    await seed_teams(test_teams_data[:3])
    
    response = await async_client.patch(f"/teams/{team_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value
    for field, expected_value in unchanged_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE TEAM
# =============================
@pytest.mark.parametrize("team_indices, team_path, expected_status", [
    # team not found
    ([], f"/teams/{BAD_ID_0000}", status.HTTP_404_NOT_FOUND),
    # invalid UUID format
    ([0], "/teams/invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_team_error_cases(async_client, seed_teams, test_teams_data, team_indices, team_path, expected_status):
    """Test DELETE team error cases (404 and 422)"""
    await conditional_seed(team_indices, test_teams_data, seed_teams)
    
    response = await async_client.delete(team_path)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_delete_team_success(async_client, seed_teams, test_teams_data):
    """Test successful team deletion with verification"""
    await seed_teams([test_teams_data[1]])

    # Test successful deletion
    response = await async_client.delete(f"/teams/{TEAM_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["team_id"] == TEAM_ID_2

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/teams/{TEAM_ID_2}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND
