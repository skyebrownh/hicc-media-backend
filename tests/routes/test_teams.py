import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_get_all_teams(async_client, test_db_pool):
    # 1. Test when no teams exist
    response1 = await async_client.get("/teams")
    assert response1.status_code == status.HTTP_200_OK
    assert isinstance(response1.json(), list)
    assert len(response1.json()) == 0
    assert response1.json() == []

    # Seed teams data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO teams (team_name, team_code)
            VALUES ('Team 1', 'team_1'),
                   ('Team 2', 'team_2'),
                   ('Team 3', 'team_3');
            """
        )

    # 2. Test when teams exist
    response2 = await async_client.get("/teams")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["team_name"] == "Team 1"
    assert response2_json[1]["team_id"] is not None
    assert response2_json[1]["team_code"] == "team_2"
    assert response2_json[2]["is_active"] is True

@pytest.mark.asyncio
async def test_get_single_team(async_client, test_db_pool):
    # 1. Test when no teams exist
    response1 = await async_client.get("/teams/58a6929c-f40d-4363-984c-4c221f41d4f0")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed teams data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('58a6929c-f40d-4363-984c-4c221f41d4f0', 'Team 1', 'team_1'),
                   ('fb4d832f-6a45-473e-b9e2-c0495938d005', 'Team 2', 'team_2'),
                   ('c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1', 'Team 3', 'team_3');
            """
        )

    # 2. Test when teams exist
    response2 = await async_client.get("/teams/fb4d832f-6a45-473e-b9e2-c0495938d005")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, dict)
    assert response2_json["team_name"] == "Team 2"
    assert response2_json["team_code"] == "team_2"
    assert response2_json["is_active"] is True

    # 3. Test team not found
    response3 = await async_client.get("/teams/00000000-0000-0000-0000-000000000000")
    assert response3.status_code == status.HTTP_404_NOT_FOUND

    # 4. Test invalid UUID format
    response4 = await async_client.get("/teams/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_create_team(async_client, test_db_pool):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"team_name": "Incomplete Team"}
    bad_payload_3 = {"team_name": "Bad Team", "team_code": 12345}  # team_code should be str
    good_payload_1 = {
        "team_name": "New Team",
        "team_code": "new_team"
    }
    
    # Seed another team data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('f8d3e340-9563-4de1-9146-675a8436242e', 'Another Team', 'another_team');
            """
        )

    bad_payload_4 = {
        "team_name": "Duplicate Team Code",
        "team_code": "new_team"  # Duplicate team_code
    }
    bad_payload_5 = {
        "team_id": "f8d3e340-9563-4de1-9146-675a8436242e",  # Duplicate team_id
        "team_name": "Duplicate ID Team",
        "team_code": "duplicate_id_team"
    }

    # 1. Test empty payload
    response1 = await async_client.post("/teams", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/teams", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid data types
    response3 = await async_client.post("/teams", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test valid payloads
    response4 = await async_client.post("/teams", json=good_payload_1)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert response4_json["team_id"] is not None
    assert response4_json["team_name"] == "New Team"
    assert response4_json["team_code"] == "new_team"
    assert response4_json["is_active"] is True

    # 5. Test duplicate team_code
    response5 = await async_client.post("/teams", json=bad_payload_4)
    assert response5.status_code == status.HTTP_409_CONFLICT

    # 6. Test duplicate team_id
    # team_id is not allowed in payload, so this raises 422 Validation Error instead of 409 Conflict
    response6 = await async_client.post("/teams", json=bad_payload_5)
    assert response6.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

# TODO: Update - full, partial, invalid, nonexistent

# TODO: Delete - nonexistent, referential integrity

# def test_update_team(test_client, setup_team):
#     setup_team_id = setup_team.get("team_id")

#     empty_json = {}
#     invalid_json2 = {"team_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"team_name": "UPDATED", "lookup": "updated"}

#     response1 = test_client.patch(f"/teams/{setup_team_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_team.get("team_name") == "TEST TEAM"

#     response2 = test_client.patch(f"/teams/{setup_team_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/teams/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/teams/{setup_team_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("team_name") == "UPDATED"
#     assert response_json.get("lookup") == "updated"

# def test_delete_team(test_client, setup_team):
#     response1 = test_client.delete(f"/teams/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/teams/{setup_team.get("team_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("team_id") == setup_team.get("team_id")
#     assert test_client.get(f"/teams/{setup_team.get("team_id")}").status_code == 404