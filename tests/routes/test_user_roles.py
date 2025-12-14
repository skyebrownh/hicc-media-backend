import pytest
from uuid import UUID
from fastapi import status
from app.db.queries import insert_all_roles_for_user, insert_all_users_for_role
from tests.utils.helpers import assert_empty_list_200

# Test data constants
USER_ID_1 = "a1b2c3d4-e5f6-4789-a012-b3c4d5e6f789"
USER_ID_2 = "b2c3d4e5-f6a7-4890-b123-c4d5e6f7a890"
USER_ID_3 = "c3d4e5f6-a7b8-4901-c234-d5e6f7a8b901"
ROLE_ID_1 = "11a2b3c4-d5e6-4789-a012-b3c4d5e6f789"
ROLE_ID_2 = "22b3c4d5-e6f7-4890-b123-c4d5e6f7a890"
ROLE_ID_3 = "33c4d5e6-f7a8-4901-c234-d5e6f7a8b901"
PROFICIENCY_ID_1 = "44d5e6f7-a8b9-4901-c234-d5e6f7a8b901"
PROFICIENCY_ID_2 = "55e6f7a8-b9c0-4901-c234-d5e6f7a8b901"

@pytest.mark.asyncio
async def test_get_roles_for_user(async_client, test_db_pool):
    # Seed users, media roles, proficiency levels, and user roles data directly into test DB
    async with test_db_pool.acquire() as conn:
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
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound'),
                   ('{ROLE_ID_3}', 'Lighting', 30, 'lighting');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Novice', 3, 'novice', true),
                   ('{PROFICIENCY_ID_2}', 'Proficient', 4, 'proficient', true);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}'),
                   ('{USER_ID_1}', '{ROLE_ID_2}', '{PROFICIENCY_ID_2}'),
                   ('{USER_ID_2}', '{ROLE_ID_3}', '{PROFICIENCY_ID_1}');
            """
        )

    # 1. Test when user has roles
    response1 = await async_client.get(f"/users/{USER_ID_1}/roles")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert response1_json[0]["user_role_id"] is not None
    assert response1_json[0]["user_id"] == USER_ID_1
    assert response1_json[0]["media_role_id"] in [ROLE_ID_1, ROLE_ID_2]
    assert response1_json[1]["user_id"] == USER_ID_1
    assert response1_json[1]["media_role_id"] in [ROLE_ID_1, ROLE_ID_2]

    # 2. Test when user has no roles
    response2 = await async_client.get(f"/users/{USER_ID_3}/roles")
    assert_empty_list_200(response2)

    # 3. Test invalid UUID format
    response3 = await async_client.get("/users/invalid-uuid-format/roles")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_get_users_for_role(async_client, test_db_pool):
    # Seed users, media roles, proficiency levels, and user roles data directly into test DB
    async with test_db_pool.acquire() as conn:
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
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound'),
                   ('{ROLE_ID_3}', 'Lighting', 30, 'lighting');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Novice', 3, 'novice', true);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}'),
                   ('{USER_ID_2}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}'),
                   ('{USER_ID_3}', '{ROLE_ID_2}', '{PROFICIENCY_ID_1}');
            """
        )

    # 1. Test when role has users
    response1 = await async_client.get(f"/roles/{ROLE_ID_1}/users")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    assert len(response1_json) == 2
    assert response1_json[0]["user_role_id"] is not None
    assert response1_json[0]["media_role_id"] == ROLE_ID_1
    assert response1_json[0]["user_id"] in [USER_ID_1, USER_ID_2]
    assert response1_json[1]["media_role_id"] == ROLE_ID_1
    assert response1_json[1]["user_id"] in [USER_ID_1, USER_ID_2]

    # 2. Test when role has no users
    response2 = await async_client.get(f"/roles/{ROLE_ID_3}/users")
    assert_empty_list_200(response2)

    # 3. Test invalid UUID format
    response3 = await async_client.get("/roles/invalid-uuid-format/users")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_get_user_role(async_client, test_db_pool):
    # Seed users, media roles, proficiency levels, and user roles data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Novice', 3, 'novice', true);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}');
            """
        )

    # 1. Test when user role exists
    response1 = await async_client.get(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, dict)
    assert response1_json["user_id"] == USER_ID_1
    assert response1_json["media_role_id"] == ROLE_ID_1
    assert response1_json["proficiency_level_id"] == PROFICIENCY_ID_1

    # 2. Test user role not found
    response2 = await async_client.get(f"/users/{USER_ID_1}/roles/{ROLE_ID_2}")
    assert response2.status_code == status.HTTP_404_NOT_FOUND
    response2 = await async_client.get(f"/users/{USER_ID_2}/roles/{ROLE_ID_1}")
    assert response2.status_code == status.HTTP_404_NOT_FOUND

    # 3. Test invalid UUID format for user_id
    response3 = await async_client.get(f"/users/invalid-uuid-format/roles/{ROLE_ID_1}")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid UUID format for role_id
    response4 = await async_client.get(f"/users/{USER_ID_1}/roles/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_user_role(async_client, test_db_pool):
    # Seed users, media roles, and proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Novice', 3, 'novice', true),
                   ('{PROFICIENCY_ID_2}', 'Proficient', 4, 'proficient', true);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"user_id": USER_ID_2}  # Missing media_role_id and proficiency_level_id
    bad_payload_3 = {"user_id": USER_ID_2, "media_role_id": ROLE_ID_2}  # Missing proficiency_level_id
    bad_payload_4 = {"user_id": "invalid-uuid", "media_role_id": ROLE_ID_2, "proficiency_level_id": PROFICIENCY_ID_1}  # Invalid UUID
    good_payload = {
        "user_id": USER_ID_2,
        "media_role_id": ROLE_ID_2,
        "proficiency_level_id": PROFICIENCY_ID_1
    }
    bad_payload_5 = {
        "user_id": USER_ID_1,
        "media_role_id": ROLE_ID_1,
        "proficiency_level_id": PROFICIENCY_ID_1  # Duplicate (already exists)
    }
    bad_payload_6 = {
        "user_id": USER_ID_2,
        "media_role_id": ROLE_ID_2,
        "proficiency_level_id": PROFICIENCY_ID_1,
        "user_role_id": "00000000-0000-0000-0000-000000000000"  # user_role_id not allowed
    }
    bad_payload_7 = {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "media_role_id": ROLE_ID_2,
        "proficiency_level_id": PROFICIENCY_ID_1  # Foreign key violation (user doesn't exist)
    }
    bad_payload_8 = {
        "user_id": USER_ID_2,
        "media_role_id": "00000000-0000-0000-0000-000000000000",
        "proficiency_level_id": PROFICIENCY_ID_1  # Foreign key violation (role doesn't exist)
    }
    bad_payload_9 = {
        "user_id": USER_ID_1,
        "media_role_id": ROLE_ID_2,
        "proficiency_level_id": "00000000-0000-0000-0000-000000000000"  # Foreign key violation (proficiency doesn't exist)
    }

    # 1. Test empty payload
    response1 = await async_client.post("/user_roles", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/user_roles", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test missing required fields (proficiency_level_id)
    response3 = await async_client.post("/user_roles", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid UUID format
    response4 = await async_client.post("/user_roles", json=bad_payload_4)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test valid payload
    response5 = await async_client.post("/user_roles", json=good_payload)
    assert response5.status_code == status.HTTP_201_CREATED
    response5_json = response5.json()
    assert response5_json["user_role_id"] is not None
    assert response5_json["user_id"] == USER_ID_2
    assert response5_json["media_role_id"] == ROLE_ID_2
    assert response5_json["proficiency_level_id"] == PROFICIENCY_ID_1

    # 6. Test duplicate user_role (same user_id + media_role_id combination)
    response6 = await async_client.post("/user_roles", json=bad_payload_5)
    assert response6.status_code == status.HTTP_409_CONFLICT

    # 7. Test extra fields not allowed in payload
    response7 = await async_client.post("/user_roles", json=bad_payload_6)
    assert response7.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 8. Test foreign key violation (user doesn't exist)
    response8 = await async_client.post("/user_roles", json=bad_payload_7)
    assert response8.status_code == status.HTTP_404_NOT_FOUND

    # 9. Test foreign key violation (role doesn't exist)
    response9 = await async_client.post("/user_roles", json=bad_payload_8)
    assert response9.status_code == status.HTTP_404_NOT_FOUND

    # 10. Test foreign key violation (proficiency doesn't exist)
    response10 = await async_client.post("/user_roles", json=bad_payload_9)
    assert response10.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_insert_all_roles_for_user_missing_untrained(async_client, test_db_pool):
    """Test inserting all roles for a user when 'untrained' proficiency level doesn't exist"""
    # Seed users and media roles, but NOT the 'untrained' proficiency level
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code, is_active)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter', true),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound', true);
            """
        )
        # Intentionally NOT creating the 'untrained' proficiency level

        # Test that inserting all roles for a user raises ValueError when 'untrained' is missing
        with pytest.raises(ValueError) as exc_info:
            await insert_all_roles_for_user(conn, user_id=UUID(USER_ID_1))
        assert "Default proficiency level 'untrained' not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_insert_all_roles_for_user(async_client, test_db_pool):
    # Seed users, media roles, and proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code, is_active)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter', true),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound', true),
                   ('{ROLE_ID_3}', 'Lighting', 30, 'lighting', false);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Untrained', 0, 'untrained', false);
            """
        )
        # Pre-existing user role for USER_ID_1
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}');
            """
        )

    # 1. Test inserting all roles for a user (should skip duplicate)
    response1 = await async_client.post(f"/users/{USER_ID_1}/roles")
    assert response1.status_code == status.HTTP_201_CREATED
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    # Should return 2 new roles (ROLE_ID_2 and ROLE_ID_3), skipping ROLE_ID_1 which already exists
    assert len(response1_json) == 2
    assert all(ur["user_id"] == USER_ID_1 for ur in response1_json)
    assert {ur["media_role_id"] for ur in response1_json} == {ROLE_ID_2, ROLE_ID_3}

    # 2. Test inserting all roles for a user with no existing roles
    response2 = await async_client.post(f"/users/{USER_ID_2}/roles")
    assert response2.status_code == status.HTTP_201_CREATED
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    # Should return all 3 roles (including inactive)
    assert len(response2_json) == 3
    assert all(ur["user_id"] == USER_ID_2 for ur in response2_json)

    # 3. Test invalid UUID format
    response3 = await async_client.post("/users/invalid-uuid-format/roles")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test user doesn't exist (foreign key violation)
    response4 = await async_client.post(f"/users/00000000-0000-0000-0000-000000000000/roles")
    assert response4.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_insert_all_users_for_role(async_client, test_db_pool):
    # Seed users, media roles, and proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone, is_active)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101', true),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102', true),
                   ('{USER_ID_3}', 'Bob', 'Johnson', '555-0103', false);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Untrained', 0, 'untrained', false);
            """
        )
        # Pre-existing user role
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}');
            """
        )

    # 1. Test inserting all users for a role (should skip duplicate)
    response1 = await async_client.post(f"/roles/{ROLE_ID_1}/users")
    assert response1.status_code == status.HTTP_201_CREATED
    response1_json = response1.json()
    assert isinstance(response1_json, list)
    # Should return 2 new users (USER_ID_2 and USER_ID_3), skipping USER_ID_1 which already exists
    assert len(response1_json) == 2
    assert all(ur["media_role_id"] == ROLE_ID_1 for ur in response1_json)
    assert {ur["user_id"] for ur in response1_json} == {USER_ID_2, USER_ID_3}

    # 2. Test inserting all users for a role with no existing users
    response2 = await async_client.post(f"/roles/{ROLE_ID_2}/users")
    assert response2.status_code == status.HTTP_201_CREATED
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    # Should return all 3 users (including inactive)
    assert len(response2_json) == 3
    assert all(ur["media_role_id"] == ROLE_ID_2 for ur in response2_json)

    # 3. Test invalid UUID format
    response3 = await async_client.post("/roles/invalid-uuid-format/users")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test role doesn't exist (foreign key violation)
    response4 = await async_client.post(f"/roles/00000000-0000-0000-0000-000000000000/users")
    assert response4.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_insert_all_users_for_role_missing_untrained(async_client, test_db_pool):
    """Test inserting all users for a role when 'untrained' proficiency level doesn't exist"""
    # Seed users and media roles, but NOT the 'untrained' proficiency level
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone, is_active)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101', true),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102', true);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter');
            """
        )
        # Intentionally NOT creating the 'untrained' proficiency level

        # Test that inserting all users for a role raises ValueError when 'untrained' is missing
        with pytest.raises(ValueError) as exc_info:
            await insert_all_users_for_role(conn, role_id=UUID(ROLE_ID_1))
        assert "Default proficiency level 'untrained' not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_user_role(async_client, test_db_pool):
    # Seed users, media roles, and proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Novice', 3, 'novice', true),
                   ('{PROFICIENCY_ID_2}', 'Proficient', 4, 'proficient', true);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"proficiency_level_id": "invalid-uuid"}  # Invalid UUID format
    good_payload = {
        "proficiency_level_id": PROFICIENCY_ID_2
    }
    bad_payload_3 = {
        "proficiency_level_id": "00000000-0000-0000-0000-000000000000"  # Foreign key violation (proficiency doesn't exist)
    }

    # 1. Test user role not found
    response1 = await async_client.patch(f"/users/{USER_ID_1}/roles/{ROLE_ID_2}", json=good_payload)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format for user_id
    response2 = await async_client.patch(f"/users/invalid-uuid-format/roles/{ROLE_ID_1}", json=good_payload)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid UUID format for role_id
    response3 = await async_client.patch(f"/users/{USER_ID_1}/roles/invalid-uuid-format", json=good_payload)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test empty payload
    response4 = await async_client.patch(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}", json=bad_payload_1)
    assert response4.status_code == status.HTTP_400_BAD_REQUEST

    # 5. Test invalid UUID format in payload
    response5 = await async_client.patch(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}", json=bad_payload_2)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload
    response6 = await async_client.patch(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}", json=good_payload)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["user_id"] == USER_ID_1
    assert response6_json["media_role_id"] == ROLE_ID_1
    assert response6_json["proficiency_level_id"] == PROFICIENCY_ID_2

    # 7. Test foreign key violation (proficiency doesn't exist)
    response7 = await async_client.patch(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}", json=bad_payload_3)
    assert response7.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_user_role(async_client, test_db_pool):
    # Seed users, media roles, and proficiency levels data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{ROLE_ID_2}', 'Sound', 20, 'sound');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, proficiency_level_code, is_assignable)
            VALUES ('{PROFICIENCY_ID_1}', 'Novice', 3, 'novice', true);
            """
        )
        await conn.execute(
            f"""
            INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
            VALUES ('{USER_ID_1}', '{ROLE_ID_1}', '{PROFICIENCY_ID_1}'),
                   ('{USER_ID_2}', '{ROLE_ID_2}', '{PROFICIENCY_ID_1}');
            """
        )

    # 1. Test user role not found
    response1 = await async_client.delete(f"/users/{USER_ID_1}/roles/{ROLE_ID_2}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format for user_id
    response2 = await async_client.delete(f"/users/invalid-uuid-format/roles/{ROLE_ID_1}")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid UUID format for role_id
    response3 = await async_client.delete(f"/users/{USER_ID_1}/roles/invalid-uuid-format")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test when user role exists
    response4 = await async_client.delete(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}")
    assert response4.status_code == status.HTTP_200_OK
    response4_json = response4.json()
    assert isinstance(response4_json, dict)
    assert response4_json["user_id"] == USER_ID_1
    assert response4_json["media_role_id"] == ROLE_ID_1

    # 5. Verify deletion by trying to get it again
    response5 = await async_client.get(f"/users/{USER_ID_1}/roles/{ROLE_ID_1}")
    assert response5.status_code == status.HTTP_404_NOT_FOUND
