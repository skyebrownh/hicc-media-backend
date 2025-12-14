import pytest
from fastapi import status
from uuid import UUID

# Test data constants
TEAM_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
TEAM_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
USER_ID_1 = "a1b2c3d4-e5f6-4789-a012-b3c4d5e6f789"
USER_ID_2 = "b2c3d4e5-f6a7-4890-b123-c4d5e6f7a890"
USER_ID_3 = "c3d4e5f6-a7b8-4901-c234-d5e6f7a8b901"

@pytest.mark.asyncio
async def test_get_all_team_users(async_client, test_db_pool):
    # 1. Test when no team users exist
    response1 = await async_client.get("/team_users")
    assert response1.status_code == status.HTTP_200_OK
    assert isinstance(response1.json(), list)
    assert len(response1.json()) == 0
    assert response1.json() == []

    # Seed teams and users data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102'),
                   ('{USER_ID_3}', 'Bob', 'Johnson', '555-0103');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO team_users (team_id, user_id)
            VALUES ('{TEAM_ID_1}', '{USER_ID_1}'),
                   ('{TEAM_ID_1}', '{USER_ID_2}'),
                   ('{TEAM_ID_2}', '{USER_ID_3}');
            """
        )

    # 2. Test when team users exist
    response2 = await async_client.get("/team_users")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["team_user_id"] is not None
    assert response2_json[0]["team_id"] == TEAM_ID_1
    assert response2_json[1]["user_id"] == USER_ID_2
    assert response2_json[2]["is_active"] is True
    assert response2_json[2]["user_id"] == USER_ID_3

@pytest.mark.asyncio
async def test_get_team_users_for_team(async_client, test_db_pool):
    # Seed teams and users data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102'),
                   ('{USER_ID_3}', 'Bob', 'Johnson', '555-0103');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO team_users (team_id, user_id)
            VALUES ('{TEAM_ID_1}', '{USER_ID_1}'),
                   ('{TEAM_ID_1}', '{USER_ID_2}');
            """
        )

    # 1. Test when team has users
    response1 = await async_client.get(f"/teams/{TEAM_ID_1}/users")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert all(tu["team_id"] == TEAM_ID_1 for tu in response1_json)
    assert {tu["user_id"] for tu in response1_json} == {USER_ID_1, USER_ID_2}

    # 2. Test when team has no users
    response2 = await async_client.get(f"/teams/{TEAM_ID_2}/users")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 0

    # 3. Test invalid UUID format
    response3 = await async_client.get("/teams/invalid-uuid-format/users")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test team not found
    response4 = await async_client.get("/teams/00000000-0000-0000-0000-000000000000/users")
    assert response4.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_single_team_user(async_client, test_db_pool):
    # Seed teams and users data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO team_users (team_id, user_id)
            VALUES ('{TEAM_ID_1}', '{USER_ID_1}');
            """
        )

    # 1. Test when team user exists
    response1 = await async_client.get(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, dict)
    assert response1_json["team_id"] == TEAM_ID_1
    assert response1_json["user_id"] == USER_ID_1
    assert response1_json["is_active"] is True
    assert response1_json["team_user_id"] is not None

    # 2. Test team user not found
    response2 = await async_client.get(f"/teams/{TEAM_ID_1}/users/{USER_ID_2}")
    assert response2.status_code == status.HTTP_404_NOT_FOUND

    # 3. Test invalid UUID format for team_id
    response3 = await async_client.get(f"/teams/invalid-uuid-format/users/{USER_ID_1}")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid UUID format for user_id
    response4 = await async_client.get(f"/teams/{TEAM_ID_1}/users/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_team_user(async_client, test_db_pool):
    # Seed teams and users data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO team_users (team_id, user_id)
            VALUES ('{TEAM_ID_1}', '{USER_ID_1}');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"team_id": TEAM_ID_1}  # Missing user_id
    bad_payload_3 = {"user_id": USER_ID_2}  # Missing team_id
    bad_payload_4 = {"team_id": "invalid-uuid", "user_id": USER_ID_2}  # Invalid UUID
    good_payload = {
        "team_id": TEAM_ID_2,
        "user_id": USER_ID_1
    }
    bad_payload_5 = {
        "team_id": TEAM_ID_1,
        "user_id": USER_ID_1  # Duplicate (already exists)
    }
    bad_payload_6 = {
        "team_id": TEAM_ID_1,
        "user_id": USER_ID_2,
        "team_user_id": "00000000-0000-0000-0000-000000000000"  # team_user_id not allowed
    }
    bad_payload_7 = {
        "team_id": "00000000-0000-0000-0000-000000000000",
        "user_id": USER_ID_2  # Foreign key violation (team doesn't exist)
    }

    # 1. Test empty payload
    response1 = await async_client.post("/team_users", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields (user_id)
    response2 = await async_client.post("/team_users", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test missing required fields (team_id)
    response3 = await async_client.post("/team_users", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid UUID format
    response4 = await async_client.post("/team_users", json=bad_payload_4)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test valid payload
    response5 = await async_client.post("/team_users", json=good_payload)
    assert response5.status_code == status.HTTP_201_CREATED
    response5_json = response5.json()
    assert response5_json["team_user_id"] is not None
    assert response5_json["team_id"] == TEAM_ID_2
    assert response5_json["user_id"] == USER_ID_1
    assert response5_json["is_active"] is True

    # 6. Test duplicate team_user (same team_id + user_id combination)
    response6 = await async_client.post("/team_users", json=bad_payload_5)
    assert response6.status_code == status.HTTP_409_CONFLICT

    # 7. Test extra fields not allowed in payload
    response7 = await async_client.post("/team_users", json=bad_payload_6)
    assert response7.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 8. Test foreign key violation (team doesn't exist)
    response8 = await async_client.post("/team_users", json=bad_payload_7)
    assert response8.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_team_user(async_client, test_db_pool):
    # Seed teams and users data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO team_users (team_id, user_id, is_active)
            VALUES ('{TEAM_ID_1}', '{USER_ID_1}', true),
                   ('{TEAM_ID_2}', '{USER_ID_2}', true);
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"is_active": "invalid"}  # is_active should be bool
    good_payload = {
        "is_active": False
    }

    # 1. Test team user not found
    response1 = await async_client.patch(f"/teams/{TEAM_ID_1}/users/{USER_ID_2}", json=good_payload)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format for team_id
    response2 = await async_client.patch(f"/teams/invalid-uuid-format/users/{USER_ID_1}", json=good_payload)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid UUID format for user_id
    response3 = await async_client.patch(f"/teams/{TEAM_ID_1}/users/invalid-uuid-format", json=good_payload)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test empty payload
    response4 = await async_client.patch(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}",json=bad_payload_1)
    assert response4.status_code == status.HTTP_400_BAD_REQUEST

    # 5. Test invalid data types
    response5 = await async_client.patch(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}", json=bad_payload_2)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload
    response6 = await async_client.patch(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}", json=good_payload)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["team_id"] == TEAM_ID_1
    assert response6_json["user_id"] == USER_ID_1
    assert response6_json["is_active"] is False

    # 7. Test update back to active
    good_payload_2 = {"is_active": True}
    response7 = await async_client.patch(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}", json=good_payload_2)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_team_user(async_client, test_db_pool):
    # Seed teams and users data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO teams (team_id, team_name, team_code)
            VALUES ('{TEAM_ID_1}', 'Team 1', 'team_1'),
                   ('{TEAM_ID_2}', 'Team 2', 'team_2');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO team_users (team_id, user_id)
            VALUES ('{TEAM_ID_1}', '{USER_ID_1}'),
                   ('{TEAM_ID_2}', '{USER_ID_2}');
            """
        )

    # 1. Test team user not found
    response1 = await async_client.delete(f"/teams/{TEAM_ID_1}/users/{USER_ID_2}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format for team_id
    response2 = await async_client.delete(f"/teams/invalid-uuid-format/users/{USER_ID_1}")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid UUID format for user_id
    response3 = await async_client.delete(f"/teams/{TEAM_ID_1}/users/invalid-uuid-format")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test when team user exists
    response4 = await async_client.delete(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}")
    assert response4.status_code == status.HTTP_200_OK
    response4_json = response4.json()
    assert isinstance(response4_json, dict)
    assert response4_json["team_id"] == TEAM_ID_1
    assert response4_json["user_id"] == USER_ID_1
    assert response4_json["is_active"] is True

    # 5. Verify deletion by trying to get it again
    response5 = await async_client.get(f"/teams/{TEAM_ID_1}/users/{USER_ID_1}")
    assert response5.status_code == status.HTTP_404_NOT_FOUND
