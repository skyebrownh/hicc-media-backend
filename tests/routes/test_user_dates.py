import pytest
from fastapi import status
from tests.seed import insert_dates
from tests.utils.helpers import assert_empty_list_200

# Test data constants
USER_ID_1 = "a1b2c3d4-e5f6-4789-a012-b3c4d5e6f789"
USER_ID_2 = "b2c3d4e5-f6a7-4890-b123-c4d5e6f7a890"
USER_ID_3 = "c3d4e5f6-a7b8-4901-c234-d5e6f7a8b901"
DATE_1 = "2025-01-15"
DATE_2 = "2025-01-20"
DATE_3 = "2025-02-01"

@pytest.mark.asyncio
async def test_get_all_user_dates(async_client, test_db_pool):
    # 1. Test when no user dates exist
    response1 = await async_client.get("/user_dates")
    assert_empty_list_200(response1)

    # Seed users and dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102'),
                   ('{USER_ID_3}', 'Bob', 'Johnson', '555-0103');
            """
        )
        await conn.execute(insert_dates([DATE_1, DATE_2, DATE_3]))
        await conn.execute(
            f"""
            INSERT INTO user_dates (user_id, date)
            VALUES ('{USER_ID_1}', '{DATE_1}'),
                   ('{USER_ID_1}', '{DATE_2}'),
                   ('{USER_ID_2}', '{DATE_3}');
            """
        )

    # 2. Test when user dates exist
    response2 = await async_client.get("/user_dates")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["user_date_id"] is not None
    assert response2_json[0]["user_id"] == USER_ID_1
    assert response2_json[0]["date"] == DATE_1
    assert response2_json[1]["user_id"] == USER_ID_1
    assert response2_json[1]["date"] == DATE_2
    assert response2_json[2]["user_id"] == USER_ID_2
    assert response2_json[2]["date"] == DATE_3

@pytest.mark.asyncio
async def test_get_single_user_date(async_client, test_db_pool):
    # Seed users and dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(insert_dates([DATE_1, DATE_2]))
        await conn.execute(
            f"""
            INSERT INTO user_dates (user_id, date)
            VALUES ('{USER_ID_1}', '{DATE_1}');
            """
        )

    # 1. Test when user date exists
    response1 = await async_client.get(f"/users/{USER_ID_1}/dates/{DATE_1}")
    assert response1.status_code == status.HTTP_200_OK
    response1_json = response1.json()
    assert isinstance(response1_json, dict)
    assert response1_json["user_id"] == USER_ID_1
    assert response1_json["date"] == DATE_1

    # 2. Test user date not found
    response2 = await async_client.get(f"/users/{USER_ID_1}/dates/{DATE_2}")
    assert response2.status_code == status.HTTP_404_NOT_FOUND

    # 3. Test invalid UUID format for user_id
    response3 = await async_client.get(f"/users/invalid-uuid-format/dates/{DATE_1}")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid date format
    response4 = await async_client.get(f"/users/{USER_ID_1}/dates/invalid-date-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_user_date(async_client, test_db_pool):
    # Seed users and dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(insert_dates([DATE_1, DATE_2]))
        await conn.execute(
            f"""
            INSERT INTO user_dates (user_id, date)
            VALUES ('{USER_ID_1}', '{DATE_1}');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"user_id": USER_ID_1}  # Missing date
    bad_payload_3 = {"date": DATE_2}  # Missing user_id
    bad_payload_4 = {"user_id": "invalid-uuid", "date": DATE_2}  # Invalid UUID
    bad_payload_5 = {"user_id": USER_ID_1, "date": "invalid-date"}  # Invalid date format
    good_payload = {
        "user_id": USER_ID_2,
        "date": DATE_1
    }
    bad_payload_6 = {
        "user_id": USER_ID_1,
        "date": DATE_1  # Duplicate (already exists)
    }
    bad_payload_7 = {
        "user_id": USER_ID_1,
        "date": DATE_2,
        "user_date_id": "00000000-0000-0000-0000-000000000000"  # user_date_id not allowed
    }
    bad_payload_8 = {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "date": DATE_2  # Foreign key violation (user doesn't exist)
    }
    bad_payload_9 = {
        "user_id": USER_ID_1,
        "date": "2025-12-31"  # Foreign key violation (date doesn't exist)
    }

    # 1. Test empty payload
    response1 = await async_client.post("/user_dates", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields (date)
    response2 = await async_client.post("/user_dates", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test missing required fields (user_id)
    response3 = await async_client.post("/user_dates", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test invalid UUID format
    response4 = await async_client.post("/user_dates", json=bad_payload_4)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test invalid date format
    response5 = await async_client.post("/user_dates", json=bad_payload_5)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload
    response6 = await async_client.post("/user_dates", json=good_payload)
    assert response6.status_code == status.HTTP_201_CREATED
    response6_json = response6.json()
    assert response6_json["user_date_id"] is not None
    assert response6_json["user_id"] == USER_ID_2
    assert response6_json["date"] == DATE_1

    # 7. Test duplicate user_date (same user_id + date combination)
    response7 = await async_client.post("/user_dates", json=bad_payload_6)
    assert response7.status_code == status.HTTP_409_CONFLICT

    # 8. Test extra fields not allowed in payload
    response8 = await async_client.post("/user_dates", json=bad_payload_7)
    assert response8.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 9. Test foreign key violation (user doesn't exist)
    response9 = await async_client.post("/user_dates", json=bad_payload_8)
    assert response9.status_code == status.HTTP_404_NOT_FOUND

    # 10. Test foreign key violation (date doesn't exist)
    response10 = await async_client.post("/user_dates", json=bad_payload_9)
    assert response10.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_insert_user_dates_bulk(async_client, test_db_pool):
    # Seed users and dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(insert_dates([DATE_1, DATE_2, DATE_3]))

    # Set up payloads
    bad_payload_1 = []
    bad_payload_2 = [{"user_id": USER_ID_1}]  # Missing date
    bad_payload_3 = [{"date": DATE_1}]  # Missing user_id
    bad_payload_4 = [
        {"user_id": USER_ID_1, "date": DATE_1},
        {"user_id": USER_ID_1, "date": DATE_2, "is_active": "False"} # is_active not allowed in payload
    ]
    good_payload = [
        {"user_id": USER_ID_1, "date": DATE_1},
        {"user_id": USER_ID_1, "date": DATE_2},
        {"user_id": USER_ID_2, "date": DATE_3}
    ]

    # 1. Test empty list
    response1 = await async_client.post("/user_dates/bulk", json=bad_payload_1)
    assert response1.status_code == status.HTTP_400_BAD_REQUEST

    # 2. Test missing required fields
    response2 = await async_client.post("/user_dates/bulk", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test missing required fields
    response3 = await async_client.post("/user_dates/bulk", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test extra fields not allowed in payload
    response4 = await async_client.post("/user_dates/bulk", json=bad_payload_4)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test valid bulk payload
    response4 = await async_client.post("/user_dates/bulk", json=good_payload)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert isinstance(response4_json, list)
    assert len(response4_json) == 3
    assert all(ud["user_date_id"] is not None for ud in response4_json)
    assert {ud["user_id"] for ud in response4_json} == {USER_ID_1, USER_ID_2}
    assert {ud["date"] for ud in response4_json} == {DATE_1, DATE_2, DATE_3}

@pytest.mark.asyncio
async def test_update_user_date(async_client, test_db_pool):
    # Seed users and dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(insert_dates([DATE_1, DATE_2, DATE_3]))
        await conn.execute(
            f"""
            INSERT INTO user_dates (user_id, date)
            VALUES ('{USER_ID_1}', '{DATE_1}');
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"date": "invalid-date"}  # Invalid date format
    good_payload = {
        "date": DATE_2
    }
    bad_payload_3 = {
        "date": "2025-12-31"  # Foreign key violation (date doesn't exist)
    }

    # 1. Test user date not found
    response1 = await async_client.patch(f"/users/{USER_ID_1}/dates/{DATE_2}", json=good_payload)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format for user_id
    response2 = await async_client.patch(f"/users/invalid-uuid-format/dates/{DATE_1}", json=good_payload)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid date format in path
    response3 = await async_client.patch(f"/users/{USER_ID_1}/dates/invalid-date-format", json=good_payload)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test empty payload
    response4 = await async_client.patch(f"/users/{USER_ID_1}/dates/{DATE_1}", json=bad_payload_1)
    assert response4.status_code == status.HTTP_400_BAD_REQUEST

    # 5. Test invalid date format in payload
    response5 = await async_client.patch(f"/users/{USER_ID_1}/dates/{DATE_1}", json=bad_payload_2)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload
    response6 = await async_client.patch(f"/users/{USER_ID_1}/dates/{DATE_1}", json=good_payload)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["user_id"] == USER_ID_1
    assert response6_json["date"] == DATE_2

    # 7. Test foreign key violation (date doesn't exist)
    response7 = await async_client.patch(f"/users/{USER_ID_1}/dates/{DATE_2}", json=bad_payload_3)
    assert response7.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_user_date(async_client, test_db_pool):
    # Seed users and dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (user_id, first_name, last_name, phone)
            VALUES ('{USER_ID_1}', 'John', 'Doe', '555-0101'),
                   ('{USER_ID_2}', 'Jane', 'Smith', '555-0102');
            """
        )
        await conn.execute(insert_dates([DATE_1, DATE_2]))
        await conn.execute(
            f"""
            INSERT INTO user_dates (user_id, date)
            VALUES ('{USER_ID_1}', '{DATE_1}'),
                   ('{USER_ID_2}', '{DATE_2}');
            """
        )

    # 1. Test user date not found
    response1 = await async_client.delete(f"/users/{USER_ID_1}/dates/{DATE_2}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format for user_id
    response2 = await async_client.delete(f"/users/invalid-uuid-format/dates/{DATE_1}")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid date format
    response3 = await async_client.delete(f"/users/{USER_ID_1}/dates/invalid-date-format")
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test when user date exists
    response4 = await async_client.delete(f"/users/{USER_ID_1}/dates/{DATE_1}")
    assert response4.status_code == status.HTTP_200_OK
    response4_json = response4.json()
    assert isinstance(response4_json, dict)
    assert response4_json["user_id"] == USER_ID_1
    assert response4_json["date"] == DATE_1

    # 5. Verify deletion by trying to get it again
    response5 = await async_client.get(f"/users/{USER_ID_1}/dates/{DATE_1}")
    assert response5.status_code == status.HTTP_404_NOT_FOUND
