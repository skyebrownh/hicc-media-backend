import pytest
from fastapi import status
from tests.seed import insert_dates
from tests.utils.helpers import assert_empty_list_200

# Test data constants
SCHEDULE_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
DATE_1 = "2025-01-15"
DATE_2 = "2025-01-20"
SCHEDULE_DATE_TYPE_ID_1 = "d0ececff-df86-404a-b2b6-8468b3b0aa33"
SCHEDULE_DATE_ID_1 = "e1e2e3e4-e5e6-4789-a012-b3c4d5e6f789"
SCHEDULE_DATE_ID_2 = "f1f2f3f4-f5f6-4890-b123-c4d5e6f7a890"
MEDIA_ROLE_ID_1 = "a1a2a3a4-a5a6-4789-a012-b3c4d5e6f789"
MEDIA_ROLE_ID_2 = "b1b2b3b4-b5b6-4890-b123-c4d5e6f7a890"
MEDIA_ROLE_ID_3 = "c1c2c3c4-c5c6-4901-c234-d5e6f7a8b901"
USER_ID_1 = "d1d2d3d4-d5d6-4901-c234-d5e6f7a8b901"
USER_ID_2 = "e1e2e3e4-e5e6-4901-c234-d5e6f7a8b901"
SCHEDULE_DATE_ROLE_ID_1 = "f1f2f3f4-f5f6-4901-c234-d5e6f7a8b901"
SCHEDULE_DATE_ROLE_ID_2 = "a9a8a7a6-a5a4-4901-c234-d5e6f7a8b901"

@pytest.mark.asyncio
async def test_get_all_schedule_date_roles(async_client, test_db_pool):
    # 1. Test when no schedule date roles exist
    response1 = await async_client.get("/schedule_date_roles")
    assert_empty_list_200(response1)

    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date)
            VALUES ('{SCHEDULE_ID_1}', '{DATE_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('{SCHEDULE_DATE_TYPE_ID_1}', 'Service', 'service');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_dates (schedule_date_id, schedule_id, date, schedule_date_type_id)
            VALUES ('{SCHEDULE_DATE_ID_1}', '{SCHEDULE_ID_1}', '{DATE_1}', '{SCHEDULE_DATE_TYPE_ID_1}'),
                   ('{SCHEDULE_DATE_ID_2}', '{SCHEDULE_ID_1}', '{DATE_2}', '{SCHEDULE_DATE_TYPE_ID_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{MEDIA_ROLE_ID_2}', 'Sound', 20, 'sound');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_roles (schedule_date_id, media_role_id, assigned_user_id)
            VALUES ('{SCHEDULE_DATE_ID_1}', '{MEDIA_ROLE_ID_1}', '{USER_ID_1}'),
                   ('{SCHEDULE_DATE_ID_1}', '{MEDIA_ROLE_ID_2}', NULL),
                   ('{SCHEDULE_DATE_ID_2}', '{MEDIA_ROLE_ID_1}', NULL);
            """
        )

    # 2. Test when schedule date roles exist
    response2 = await async_client.get("/schedule_date_roles")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["schedule_date_role_id"] is not None
    assert response2_json[0]["schedule_date_id"] == SCHEDULE_DATE_ID_1
    assert response2_json[0]["media_role_id"] in [MEDIA_ROLE_ID_1, MEDIA_ROLE_ID_2]
    assert response2_json[1]["is_active"] is True

@pytest.mark.asyncio
async def test_get_single_schedule_date_role(async_client, test_db_pool):
    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1]))
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date)
            VALUES ('{SCHEDULE_ID_1}', '{DATE_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('{SCHEDULE_DATE_TYPE_ID_1}', 'Service', 'service');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_dates (schedule_date_id, schedule_id, date, schedule_date_type_id)
            VALUES ('{SCHEDULE_DATE_ID_1}', '{SCHEDULE_ID_1}', '{DATE_1}', '{SCHEDULE_DATE_TYPE_ID_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'ProPresenter', 10, 'propresenter');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_roles (schedule_date_role_id, schedule_date_id, media_role_id)
            VALUES ('{SCHEDULE_DATE_ROLE_ID_1}', '{SCHEDULE_DATE_ID_1}', '{MEDIA_ROLE_ID_1}');
            """
        )

    # 1. Test when schedule date role exists
    response1 = await async_client.get(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, dict)
    assert response1_json["schedule_date_role_id"] == SCHEDULE_DATE_ROLE_ID_1
    assert response1_json["schedule_date_id"] == SCHEDULE_DATE_ID_1
    assert response1_json["media_role_id"] == MEDIA_ROLE_ID_1
    assert response1_json["is_required"] is True
    assert response1_json["is_preferred"] is False
    assert response1_json["is_active"] is True

    # 2. Test schedule date role not found
    response2 = await async_client.get("/schedule_date_roles/00000000-0000-0000-0000-000000000000")
    assert response2.status_code == status.HTTP_404_NOT_FOUND

    # 3. Test invalid UUID format
    response3 = await async_client.get("/schedule_date_roles/invalid-uuid-format")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_schedule_date_role(async_client, test_db_pool):
    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1, DATE_2]))
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date)
            VALUES ('{SCHEDULE_ID_1}', '{DATE_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('{SCHEDULE_DATE_TYPE_ID_1}', 'Service', 'service');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_dates (schedule_date_id, schedule_id, date, schedule_date_type_id)
            VALUES ('{SCHEDULE_DATE_ID_1}', '{SCHEDULE_ID_1}', '{DATE_1}', '{SCHEDULE_DATE_TYPE_ID_1}'),
                   ('{SCHEDULE_DATE_ID_2}', '{SCHEDULE_ID_1}', '{DATE_2}', '{SCHEDULE_DATE_TYPE_ID_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{MEDIA_ROLE_ID_2}', 'Sound', 20, 'sound'),
                   ('{MEDIA_ROLE_ID_3}', 'Lighting', 30, 'lighting');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_roles (schedule_date_id, media_role_id, assigned_user_id)
            VALUES ('{SCHEDULE_DATE_ID_1}', '{MEDIA_ROLE_ID_1}', '{USER_ID_1}');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"schedule_date_id": SCHEDULE_DATE_ID_1}  # Missing media_role_id
    bad_payload_3 = {"media_role_id": MEDIA_ROLE_ID_2}  # Missing schedule_date_id
    bad_payload_4 = {"schedule_date_id": "invalid-uuid", "media_role_id": MEDIA_ROLE_ID_2}  # Invalid UUID
    good_payload = {
        "schedule_date_id": SCHEDULE_DATE_ID_1,
        "media_role_id": MEDIA_ROLE_ID_2
    }
    bad_payload_5 = {
        "schedule_date_id": SCHEDULE_DATE_ID_1,
        "media_role_id": MEDIA_ROLE_ID_1,
        "assigned_user_id": USER_ID_1  # Duplicate (same schedule_date_id + media_role_id + assigned_user_id combination)
    }
    bad_payload_6 = {
        "schedule_date_id": SCHEDULE_DATE_ID_1,
        "media_role_id": MEDIA_ROLE_ID_2,
        "schedule_date_role_id": "00000000-0000-0000-0000-000000000000"  # schedule_date_role_id not allowed
    }
    bad_payload_7 = {
        "schedule_date_id": "00000000-0000-0000-0000-000000000000",
        "media_role_id": MEDIA_ROLE_ID_2  # Foreign key violation (schedule_date doesn't exist)
    }
    bad_payload_8 = {
        "schedule_date_id": SCHEDULE_DATE_ID_1,
        "media_role_id": "00000000-0000-0000-0000-000000000000"  # Foreign key violation (media_role doesn't exist)
    }
    bad_payload_9 = {
        "schedule_date_id": SCHEDULE_DATE_ID_1,
        "media_role_id": MEDIA_ROLE_ID_2,
        "assigned_user_id": "00000000-0000-0000-0000-000000000000"  # Foreign key violation (user doesn't exist)
    }
    good_payload_with_optional = {
        "schedule_date_id": SCHEDULE_DATE_ID_2,
        "media_role_id": MEDIA_ROLE_ID_3,
        "assigned_user_id": USER_ID_2,
        "is_required": False,
        "is_preferred": True
    }

    # 1. Test empty payload
    response1 = await async_client.post("/schedule_date_roles", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/schedule_date_roles", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test missing required fields
    response3 = await async_client.post("/schedule_date_roles", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid UUID format
    response4 = await async_client.post("/schedule_date_roles", json=bad_payload_4)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test valid payload
    response5 = await async_client.post("/schedule_date_roles", json=good_payload)
    assert response5.status_code == status.HTTP_201_CREATED
    response5_json = response5.json()
    assert response5_json["schedule_date_role_id"] is not None
    assert response5_json["schedule_date_id"] == SCHEDULE_DATE_ID_1
    assert response5_json["media_role_id"] == MEDIA_ROLE_ID_2
    assert response5_json["is_required"] is False
    assert response5_json["is_preferred"] is False
    assert response5_json["is_active"] is True

    # 6. Test duplicate schedule_date_role (same media_role_id + schedule_date_id + assigned_user_id combination)
    response6 = await async_client.post("/schedule_date_roles", json=bad_payload_5)
    assert response6.status_code == status.HTTP_409_CONFLICT

    # 7. Test extra fields not allowed in payload
    response7 = await async_client.post("/schedule_date_roles", json=bad_payload_6)
    assert response7.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 8. Test foreign key violation (schedule_date doesn't exist)
    response8 = await async_client.post("/schedule_date_roles", json=bad_payload_7)
    assert response8.status_code == status.HTTP_404_NOT_FOUND

    # 9. Test foreign key violation (media_role doesn't exist)
    response9 = await async_client.post("/schedule_date_roles", json=bad_payload_8)
    assert response9.status_code == status.HTTP_404_NOT_FOUND

    # 10. Test foreign key violation (user doesn't exist)
    response10 = await async_client.post("/schedule_date_roles", json=bad_payload_9)
    assert response10.status_code == status.HTTP_404_NOT_FOUND

    # 11. Test valid payload with optional fields
    response11 = await async_client.post("/schedule_date_roles", json=good_payload_with_optional)
    assert response11.status_code == status.HTTP_201_CREATED
    response11_json = response11.json()
    assert response11_json["assigned_user_id"] == USER_ID_2
    assert response11_json["is_required"] is False
    assert response11_json["is_preferred"] is True

@pytest.mark.asyncio
async def test_update_schedule_date_role(async_client, test_db_pool):
    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1]))
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date)
            VALUES ('{SCHEDULE_ID_1}', '{DATE_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('{SCHEDULE_DATE_TYPE_ID_1}', 'Service', 'service');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_dates (schedule_date_id, schedule_id, date, schedule_date_type_id)
            VALUES ('{SCHEDULE_DATE_ID_1}', '{SCHEDULE_ID_1}', '{DATE_1}', '{SCHEDULE_DATE_TYPE_ID_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'ProPresenter', 10, 'propresenter');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_roles (schedule_date_role_id, schedule_date_id, media_role_id, assigned_user_id, is_required, is_preferred)
            VALUES ('{SCHEDULE_DATE_ROLE_ID_1}', '{SCHEDULE_DATE_ID_1}', '{MEDIA_ROLE_ID_1}', '{USER_ID_1}', true, false);
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    good_payload_1 = {"assigned_user_id": USER_ID_2}
    good_payload_2 = {"is_required": False}
    good_payload_3 = {"is_preferred": True}
    good_payload_4 = {"is_active": False}
    bad_payload_2 = {"assigned_user_id": "00000000-0000-0000-0000-000000000000"}  # Foreign key violation (user doesn't exist)

    # 1. Test schedule date role not found
    response1 = await async_client.patch("/schedule_date_roles/00000000-0000-0000-0000-000000000000", json=good_payload_1)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/schedule_date_roles/invalid-uuid-format", json=good_payload_1)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test valid payload (update assigned_user_id)
    response4 = await async_client.patch(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}", json=good_payload_1)
    assert response4.status_code == status.HTTP_200_OK
    response4_json = response4.json()
    assert response4_json["assigned_user_id"] == USER_ID_2

    # 5. Test valid payload (update is_required)
    response5 = await async_client.patch(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}", json=good_payload_2)
    assert response5.status_code == status.HTTP_200_OK
    response5_json = response5.json()
    assert response5_json["is_required"] is False

    # 6. Test valid payload (update is_preferred)
    response6 = await async_client.patch(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}", json=good_payload_3)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["is_preferred"] is True

    # 7. Test valid payload (update is_active)
    response7 = await async_client.patch(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}", json=good_payload_4)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["is_active"] is False

    # 8. Test foreign key violation (user doesn't exist)
    response8 = await async_client.patch(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}", json=bad_payload_2)
    assert response8.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_schedule_date_role(async_client, test_db_pool):
    # Seed data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_1]))
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date)
            VALUES ('{SCHEDULE_ID_1}', '{DATE_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('{SCHEDULE_DATE_TYPE_ID_1}', 'Service', 'service');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_dates (schedule_date_id, schedule_id, date, schedule_date_type_id)
            VALUES ('{SCHEDULE_DATE_ID_1}', '{SCHEDULE_ID_1}', '{DATE_1}', '{SCHEDULE_DATE_TYPE_ID_1}');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO media_roles (media_role_id, media_role_name, sort_order, media_role_code)
            VALUES ('{MEDIA_ROLE_ID_1}', 'ProPresenter', 10, 'propresenter'),
                   ('{MEDIA_ROLE_ID_2}', 'Sound', 20, 'sound');
            """
        )
        await conn.execute(
            f"""
            INSERT INTO schedule_date_roles (schedule_date_role_id, schedule_date_id, media_role_id)
            VALUES ('{SCHEDULE_DATE_ROLE_ID_1}', '{SCHEDULE_DATE_ID_1}', '{MEDIA_ROLE_ID_1}'),
                   ('{SCHEDULE_DATE_ROLE_ID_2}', '{SCHEDULE_DATE_ID_1}', '{MEDIA_ROLE_ID_2}');
            """
        )

    # 1. Test schedule date role not found
    response1 = await async_client.delete("/schedule_date_roles/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/schedule_date_roles/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when schedule date role exists
    response3 = await async_client.delete(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["schedule_date_role_id"] == SCHEDULE_DATE_ROLE_ID_1

    # 4. Verify deletion by trying to get it again
    response4 = await async_client.get(f"/schedule_date_roles/{SCHEDULE_DATE_ROLE_ID_1}")
    assert response4.status_code == status.HTTP_404_NOT_FOUND
