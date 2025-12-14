import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200

TEAM_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
TEAM_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
TEAM_ID_3 = "c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1"
TEAM_ID_4 = "e1fdfd00-e097-415b-c3c7-9579c4c1bb44"

@pytest.mark.asyncio
async def test_get_all_teams(async_client, test_db_pool):
    # 1. Test when no teams exist
    response1 = await async_client.get("/teams")
    assert_empty_list_200(response1)

    # Seed teams data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
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
    response1 = await async_client.get(f"/teams/{TEAM_ID_1}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed teams data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2'),
                   ('{TEAM_ID_3}', 'Team 3', 'team_3');
            """
        )

    # 2. Test when teams exist
    response2 = await async_client.get(f"/teams/{TEAM_ID_2}")
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
async def test_insert_team(async_client, test_db_pool):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"team_name": "Incomplete Team"}
    bad_payload_3 = {"team_name": "Bad Team", "team_code": 12345}  # team_code should be str
    good_payload = {
        "team_name": "New Team",
        "team_code": "new_team"
    }
    
    # Seed another team data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_4}', 'Another Team', 'another_team');
            """
        )

    bad_payload_4 = {
        "team_name": "Duplicate Team Code",
        "team_code": "new_team"  # Duplicate team_code
    }
    bad_payload_5 = {
        "team_id": TEAM_ID_4,  # team_id not allowed in payload
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

    # 4. Test valid payload
    response4 = await async_client.post("/teams", json=good_payload)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert response4_json["team_id"] is not None
    assert response4_json["team_name"] == "New Team"
    assert response4_json["team_code"] == "new_team"
    assert response4_json["is_active"] is True

    # 5. Test duplicate team_code
    response5 = await async_client.post("/teams", json=bad_payload_4)
    assert response5.status_code == status.HTTP_409_CONFLICT

    # 6. Test team_id not allowed in payload
    # team_id is not allowed in payload, so this raises 422 Validation Error instead of 409 Conflict
    response6 = await async_client.post("/teams", json=bad_payload_5)
    assert response6.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_update_team(async_client, test_db_pool):
    # Seed team data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2'),
                   ('{TEAM_ID_3}', 'Team 3', 'team_3');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"team_name": 12345}  # team_name should be str
    bad_payload_3 = {"team_name": "Invalid", "team_code": "invalid"}  # team_code is not updatable
    good_payload_full = {
        "team_name": "Updated Team Name",
        "is_active": False
    }
    good_payload_partial_1 = {
        "is_active": False
    }
    good_payload_partial_2 = {
        "team_name": "Partially Updated Team"
    }

    # 1. Test team not found
    response1 = await async_client.patch("/teams/00000000-0000-0000-0000-000000000000", json=good_payload_full)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/teams/invalid-uuid-format", json=good_payload_full)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/teams/{TEAM_ID_3}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch(f"/teams/{TEAM_ID_3}", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test non-updatable field
    response5 = await async_client.patch(f"/teams/{TEAM_ID_3}", json=bad_payload_3)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload to update full record
    response6 = await async_client.patch(f"/teams/{TEAM_ID_3}", json=good_payload_full)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["team_name"] == "Updated Team Name"
    assert response6_json["team_code"] == "team_3"
    assert response6_json["is_active"] is False

    # 7. Test valid payload to update partial record (is_active only)
    response7 = await async_client.patch(f"/teams/{TEAM_ID_2}", json=good_payload_partial_1)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["team_name"] == "Team 2"
    assert response7_json["team_code"] == "team_2"
    assert response7_json["is_active"] is False 

    # 8. Test valid payload to update partial record (team_name only)
    response8 = await async_client.patch(f"/teams/{TEAM_ID_1}", json=good_payload_partial_2)
    assert response8.status_code == status.HTTP_200_OK
    response8_json = response8.json()
    assert response8_json["team_name"] == "Partially Updated Team"
    assert response8_json["team_code"] == "team_1"
    assert response8_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_team(async_client, test_db_pool):
    # Seed teams data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2'),
                   ('{TEAM_ID_3}', 'Team 3', 'team_3');
            """
        )

    # 1. Test team not found
    response1 = await async_client.delete("/teams/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/teams/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when teams exist
    response3 = await async_client.delete(f"/teams/{TEAM_ID_2}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["team_name"] == "Team 2"
    assert response3_json["team_code"] == "team_2"
    assert response3_json["is_active"] is True