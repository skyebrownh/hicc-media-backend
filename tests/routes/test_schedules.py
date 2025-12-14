import pytest
from fastapi import status
from tests.seed import insert_dates
from tests.utils.helpers import assert_empty_list_200

SCHEDULE_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
SCHEDULE_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
SCHEDULE_ID_3 = "c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1"
SCHEDULE_DATE_TYPE_ID_1 = "d0ececff-df86-404a-b2b6-8468b3b0aa33"
SCHEDULE_ID_1 = "a1b2c3d4-e5f6-4789-a012-b3c4d5e6f789"

@pytest.mark.asyncio
async def test_get_all_schedules(async_client, test_db_pool):
    # 1. Test when no schedules exist
    response1 = await async_client.get("/schedules")
    assert_empty_list_200(response1)

    # Seed schedules data directly into test DB
    async with test_db_pool.acquire() as conn:
        # Insert required dates for foreign key constraint
        await conn.execute(insert_dates(["2025-01-01", "2025-02-01", "2025-03-01"]))
        # Insert schedules
        await conn.execute(
            f"""
            INSERT INTO schedules (month_start_date, notes)
            VALUES ('2025-01-01', 'First schedule'),
                   ('2025-02-01', 'Second schedule'),
                   ('2025-03-01', NULL);
            """
        )

    # 2. Test when schedules exist
    response2 = await async_client.get("/schedules")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["month_start_date"] == "2025-01-01"
    assert response2_json[1]["schedule_id"] is not None
    assert response2_json[1]["notes"] == "Second schedule"
    assert response2_json[2]["is_active"] is True

@pytest.mark.asyncio
async def test_get_all_schedule_dates_for_schedule(async_client, test_db_pool):
    # Seed schedules data directly into test DB
    async with test_db_pool.acquire() as conn:
        # Insert required dates for foreign key constraint
        await conn.execute(insert_dates(["2025-05-01", "2025-05-02", "2025-05-03"]))
        # Insert schedules
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date, notes)
            VALUES ('{SCHEDULE_ID_1}', '2025-05-01', 'First schedule');
            """
        )
        # Insert schedule_date_type
        await conn.execute(
            f"""
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('{SCHEDULE_DATE_TYPE_ID_1}', 'Service', 'service');
            """
        )

    # 1. Test when no schedule_dates exist
    response1 = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert_empty_list_200(response1)

    # Insert schedule_dates
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO schedule_dates (schedule_id, date, schedule_date_type_id)
            VALUES 
                ('{SCHEDULE_ID_1}', '2025-05-01', '{SCHEDULE_DATE_TYPE_ID_1}'),
                ('{SCHEDULE_ID_1}', '2025-05-02', '{SCHEDULE_DATE_TYPE_ID_1}'),
                ('{SCHEDULE_ID_1}', '2025-05-03', '{SCHEDULE_DATE_TYPE_ID_1}');
            """
        )
    
    # 2. Test when schedule_dates exist
    response2 = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    assert len(response2_json) == 3
    assert response2_json[0]["date"] == "2025-05-01"
    assert response2_json[1]["date"] == "2025-05-02"
    assert response2_json[2]["date"] == "2025-05-03"
    assert response2_json[1]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
    assert response2_json[1]["notes"] is None
    assert response2_json[2]["is_active"] is True

@pytest.mark.asyncio
async def test_get_single_schedule(async_client, test_db_pool):
    # 1. Test when no schedules exist
    response1 = await async_client.get(f"/schedules/{SCHEDULE_ID_1}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed schedules data directly into test DB
    async with test_db_pool.acquire() as conn:
        # Insert required dates for foreign key constraint
        await conn.execute(insert_dates(["2025-01-01", "2025-02-01", "2025-03-01"]))
        # Insert schedules
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date, notes)
            VALUES ('{SCHEDULE_ID_1}', '2025-01-01', 'First schedule'),
                   ('{SCHEDULE_ID_2}', '2025-02-01', 'Second schedule'),
                   ('{SCHEDULE_ID_3}', '2025-03-01', NULL);
            """
        )

    # 2. Test when schedules exist
    response2 = await async_client.get(f"/schedules/{SCHEDULE_ID_2}")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, dict)
    assert response2_json["month_start_date"] == "2025-02-01"
    assert response2_json["notes"] == "Second schedule"
    assert response2_json["is_active"] is True

    # 3. Test schedule not found
    response3 = await async_client.get("/schedules/00000000-0000-0000-0000-000000000000")
    assert response3.status_code == status.HTTP_404_NOT_FOUND

    # 4. Test invalid UUID format
    response4 = await async_client.get("/schedules/invalid-uuid-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_schedule(async_client, test_db_pool):
    # Seed dates data directly into test DB for foreign key constraint testing
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates(["2025-05-01"]))

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"notes": "missing required month_start_date"} # missing required field
    bad_payload_3 = {"month_start_date": 12345, "notes": 999}  # wrong types
    bad_payload_4 = {
        "schedule_id": "f8d3e340-9563-4de1-9146-675a8436242e",  # Not allowed in payload
        "month_start_date": "2025-05-01"
    }
    bad_payload_5 = {"month_start_date": "2000-01-01"}  # foreign key constraint violation
    good_payload = {
        "month_start_date": "2025-05-01",
        "notes": "New schedule"
    }

    # 1. Test empty payload
    response1 = await async_client.post("/schedules", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test missing required fields
    response2 = await async_client.post("/schedules", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid data types
    response3 = await async_client.post("/schedules", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test schedule_id in payload (should be forbidden)
    response4 = await async_client.post("/schedules", json=bad_payload_4)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # 5. Test foreign key constraint violation
    response5 = await async_client.post("/schedules", json=bad_payload_5)
    assert response5.status_code == status.HTTP_404_NOT_FOUND

    # 6. Test valid payload
    response6 = await async_client.post("/schedules", json=good_payload)
    assert response6.status_code == status.HTTP_201_CREATED
    response6_json = response6.json()
    assert response6_json["schedule_id"] is not None
    assert response6_json["month_start_date"] == "2025-05-01"
    assert response6_json["notes"] == "New schedule"
    assert response6_json["is_active"] is True

@pytest.mark.asyncio
async def test_update_schedule(async_client, test_db_pool):
    # Seed schedule data directly into test DB
    async with test_db_pool.acquire() as conn:
        # Insert required dates for foreign key constraint
        await conn.execute(insert_dates(["2025-01-01", "2025-02-01", "2025-03-01"]))
        # Insert schedules
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date, notes)
            VALUES ('{SCHEDULE_ID_1}', '2025-01-01', 'First schedule'),
                   ('{SCHEDULE_ID_2}', '2025-02-01', 'Second schedule'),
                   ('{SCHEDULE_ID_3}', '2025-03-01', NULL);
            """
        )

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"month_start_date": 12345}  # month_start_date should be str/date
    bad_payload_3 = {"schedule_id": SCHEDULE_ID_1}  # schedule_id is not updatable
    good_payload_full = {
        "notes": "Updated schedule",
        "is_active": False
    }
    good_payload_partial_1 = {
        "is_active": False
    }
    good_payload_partial_2 = {
        "notes": "Partially Updated"
    }

    # 1. Test schedule not found
    response1 = await async_client.patch("/schedules/00000000-0000-0000-0000-000000000000", json=good_payload_full)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.patch("/schedules/invalid-uuid-format", json=good_payload_full)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/schedules/{SCHEDULE_ID_3}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch(f"/schedules/{SCHEDULE_ID_3}", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test non-updatable field
    response5 = await async_client.patch(f"/schedules/{SCHEDULE_ID_3}", json=bad_payload_3)
    assert response5.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 6. Test valid payload to update full record
    response6 = await async_client.patch(f"/schedules/{SCHEDULE_ID_3}", json=good_payload_full)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["month_start_date"] == "2025-03-01"
    assert response6_json["notes"] == "Updated schedule"
    assert response6_json["is_active"] is False

    # 7. Test valid payload to update partial record (is_active only)
    response7 = await async_client.patch(f"/schedules/{SCHEDULE_ID_2}", json=good_payload_partial_1)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["month_start_date"] == "2025-02-01"
    assert response7_json["is_active"] is False

    # 8. Test valid payload to update partial record (notes only)
    response8 = await async_client.patch(f"/schedules/{SCHEDULE_ID_1}", json=good_payload_partial_2)
    assert response8.status_code == status.HTTP_200_OK
    response8_json = response8.json()
    assert response8_json["notes"] == "Partially Updated"
    assert response8_json["is_active"] is True

@pytest.mark.asyncio
async def test_delete_schedule(async_client, test_db_pool):
    # Seed schedules data directly into test DB
    async with test_db_pool.acquire() as conn:
        # Insert required dates for foreign key constraint
        await conn.execute(insert_dates(["2025-01-01", "2025-02-01", "2025-03-01"]))
        # Insert schedules
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date, notes)
            VALUES ('{SCHEDULE_ID_1}', '2025-01-01', 'First schedule'),
                   ('{SCHEDULE_ID_2}', '2025-02-01', 'Second schedule'),
                   ('{SCHEDULE_ID_3}', '2025-03-01', NULL);
            """
        )

    # 1. Test schedule not found
    response1 = await async_client.delete("/schedules/00000000-0000-0000-0000-000000000000")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/schedules/invalid-uuid-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when schedules exist
    response3 = await async_client.delete(f"/schedules/{SCHEDULE_ID_2}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["month_start_date"] == "2025-02-01"
    assert response3_json["schedule_id"] == SCHEDULE_ID_2

@pytest.mark.asyncio
async def test_delete_schedule_dates_for_schedule(async_client, test_db_pool):
    # Seed schedules data directly into test DB
    async with test_db_pool.acquire() as conn:
        # Insert required dates for foreign key constraint
        await conn.execute(insert_dates(["2025-05-01"]))
        # Insert schedules
        await conn.execute(
            f"""
            INSERT INTO schedules (schedule_id, month_start_date, notes)
            VALUES ('{SCHEDULE_ID_1}', '2025-05-01', 'First schedule');
            """
        )
        # Insert schedule_date_type
        await conn.execute(
            f"""
            INSERT INTO schedule_date_types (schedule_date_type_id, schedule_date_type_name, schedule_date_type_code)
            VALUES ('{SCHEDULE_DATE_TYPE_ID_1}', 'Service', 'service');
            """
        )

    # 1. Test schedule not found
    response1 = await async_client.delete("/schedules/00000000-0000-0000-0000-000000000000/schedule_dates")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid UUID format
    response2 = await async_client.delete("/schedules/invalid-uuid-format/schedule_dates")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when no schedule_dates exist
    response3 = await async_client.delete(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, list)
    assert len(response3_json) == 0
    assert response3_json == []

    # Insert schedule_dates
    async with test_db_pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO schedule_dates (schedule_id, date, schedule_date_type_id)
            VALUES 
                ('{SCHEDULE_ID_1}', '2025-05-01', '{SCHEDULE_DATE_TYPE_ID_1}');
            """
        )

    # 3. Test when schedule_dates exist
    response4 = await async_client.delete(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert response4.status_code == status.HTTP_200_OK
    response4_json = response4.json()
    assert isinstance(response4_json, list)
    assert len(response4_json) == 1
    assert response4_json[0]["date"] == "2025-05-01"
    assert response4_json[0]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1

    # 4. Verify deletion by trying to get it again
    response5 = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
    assert_empty_list_200(response5)