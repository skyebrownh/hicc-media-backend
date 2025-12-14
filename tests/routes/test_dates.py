import pytest
import datetime
from fastapi import status
from tests.seed import insert_dates
from tests.utils.helpers import assert_empty_list_200

DATE_1 = "2024-02-29"
DATE_2 = "2025-01-01"
DATE_3 = "2025-01-05"
DATE_4 = "2025-03-31"
DATE_5 = "2025-05-01"
DATE_6 = "2025-06-06"
DATE_7 = "2025-09-08"
DATE_8 = "2025-12-31"

@pytest.mark.asyncio
async def test_get_all_dates(async_client, test_db_pool):
    # 1. Test when no dates exist
    response1 = await async_client.get("/dates")
    assert_empty_list_200(response1)

    # Seed dates data directly into test DB with more edge-case variety
    varied_dates = [
        DATE_1,  # Leap year, last day of Feb
        DATE_2,  # Wednesday, first day of year & month
        DATE_3,  # Sunday, first Sunday in Jan (test is_weekend + 5th day of month)
        DATE_5,  # Thursday, first of May
        DATE_7,  # Monday, second Monday of Sep
        DATE_8,  # Last day of year & Dec, Wednesday
    ]
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates(varied_dates))

    response2 = await async_client.get("/dates")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, list)
    returned_dates = [d["date"] for d in response2_json]
    # All inserted dates should be present
    for d in varied_dates:
        assert d in returned_dates
    assert len(response2_json) == len(varied_dates) 

    # Cross-check specifics for edge cases - assert all date fields at least once, but only where necessary
    for row in response2_json:
        d = row["date"]
        if d == DATE_2:  # first of year/month
            assert row["calendar_year"] == 2025
            assert row["calendar_month"] == 1
            assert row["calendar_day"] == 1
            assert row["month_name"].lower() == "january"
            assert row["month_abbr"].lower() == "jan"
            assert row["weekday"] == 2  # Wednesday
            assert row["weekday_name"].lower() == "wednesday"
            assert row["is_first_of_month"] is True
            assert row["is_last_of_month"] is False
            assert row["calendar_quarter"] == 1
        elif d == DATE_3:  # first Sunday of Jan
            assert row["is_weekend"] is True
            assert row["is_weekday"] is False
            assert row["weekday_of_month"] == 1
        elif d == DATE_1:  # leap year, last day Feb
            assert row["is_last_of_month"] is True
            assert row["calendar_day"] == 29
        elif d == DATE_8:  # last of year/month
            assert row["is_last_of_month"] is True
        elif d == DATE_5:  # first of May
            assert row["is_first_of_month"] is True
        elif d == DATE_7:  # second Monday September
            assert row["weekday_of_month"] == 2

@pytest.mark.asyncio
async def test_get_single_date(async_client, test_db_pool):
    # 1. Test when no dates exist
    response1 = await async_client.get(f"/dates/{DATE_2}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # Seed dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_3]))

    # 2. Test when dates exist
    response2 = await async_client.get(f"/dates/{DATE_3}")
    assert response2.status_code == status.HTTP_200_OK
    response2_json = response2.json()
    assert isinstance(response2_json, dict)
    assert response2_json["date"] == DATE_3

    # 3. Test date not found
    response3 = await async_client.get(f"/dates/{DATE_8}")
    assert response3.status_code == status.HTTP_404_NOT_FOUND

    # 4. Test invalid date format
    response4 = await async_client.get("/dates/invalid-date-format")
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_date(async_client, test_db_pool):
    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"date": "invalid-date"}  # Invalid date format
    bad_payload_3 = {"date": 12345}  # date should be date string
    good_payload = {
        "date": DATE_5
    }
    
    # Seed another date data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_6]))

    bad_payload_4 = {
        "date": DATE_5  # Duplicate date (will be inserted in test 4)
    }
    bad_payload_5 = {
        "date": DATE_7,
        "calendar_year": 2025  # calendar_year not allowed in payload
    }

    # 1. Test empty payload
    response1 = await async_client.post("/dates", json=bad_payload_1)
    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 2. Test invalid date format
    response2 = await async_client.post("/dates", json=bad_payload_2)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test invalid data types
    response3 = await async_client.post("/dates", json=bad_payload_3)
    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 4. Test valid payload
    response4 = await async_client.post("/dates", json=good_payload)
    assert response4.status_code == status.HTTP_201_CREATED
    response4_json = response4.json()
    assert response4_json["date"] == DATE_5

    assert response4_json["calendar_month"] == 5
    assert response4_json["calendar_day"] == 1
    # Check that auto-generated fields exist
    assert "is_weekend" in response4_json
    assert "is_weekday" in response4_json
    assert "weekday" in response4_json

    # 5. Test duplicate date
    response5 = await async_client.post("/dates", json=bad_payload_4)
    assert response5.status_code == status.HTTP_409_CONFLICT

    # 6. Test extra fields not allowed in payload
    # Extra fields are not allowed in payload, so this raises 422 Validation Error
    response6 = await async_client.post("/dates", json=bad_payload_5)
    assert response6.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_update_date(async_client, test_db_pool):
    # Seed date data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_2, DATE_3, DATE_4]))

    # Set up payloads
    bad_payload_1 = {}
    bad_payload_2 = {"calendar_year": "invalid"}  # calendar_year should be int
    good_payload_full = {
        "is_holiday": True,
        "is_weekend": False
    }
    good_payload_partial_1 = {
        "is_holiday": True
    }
    good_payload_partial_2 = {
        "calendar_year": 2026
    }

    # 1. Test date not found
    response1 = await async_client.patch(f"/dates/{DATE_8}", json=good_payload_full)
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid date format
    response2 = await async_client.patch("/dates/invalid-date-format", json=good_payload_full)
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test empty payload
    response3 = await async_client.patch(f"/dates/{DATE_4}", json=bad_payload_1)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Test invalid data types
    response4 = await async_client.patch(f"/dates/{DATE_4}", json=bad_payload_2)
    assert response4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 5. Test valid payload to update full record
    response5 = await async_client.patch(f"/dates/{DATE_4}", json=good_payload_full)
    assert response5.status_code == status.HTTP_200_OK
    response5_json = response5.json()
    assert response5_json["is_holiday"] is True
    assert response5_json["is_weekend"] is False

    # 6. Test valid payload to update partial record (is_holiday only)
    response6 = await async_client.patch(f"/dates/{DATE_3}", json=good_payload_partial_1)
    assert response6.status_code == status.HTTP_200_OK
    response6_json = response6.json()
    assert response6_json["is_holiday"] is True
    # Other fields should remain unchanged
    assert response6_json["calendar_year"] == 2025

    # 7. Test valid payload to update partial record (calendar_year only)
    response7 = await async_client.patch(f"/dates/{DATE_2}", json=good_payload_partial_2)
    assert response7.status_code == status.HTTP_200_OK
    response7_json = response7.json()
    assert response7_json["calendar_year"] == 2026

@pytest.mark.asyncio
async def test_delete_date(async_client, test_db_pool):
    # Seed dates data directly into test DB
    async with test_db_pool.acquire() as conn:
        await conn.execute(insert_dates([DATE_3]))

    # 1. Test date not found
    response1 = await async_client.delete(f"/dates/{DATE_8}")
    assert response1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Test invalid date format
    response2 = await async_client.delete("/dates/invalid-date-format")
    assert response2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 3. Test when dates exist
    response3 = await async_client.delete(f"/dates/{DATE_3}")
    assert response3.status_code == status.HTTP_200_OK
    response3_json = response3.json()
    assert isinstance(response3_json, dict)
    assert response3_json["date"] == DATE_3

    # 4. Verify deletion by trying to get it again
    response4 = await async_client.get(f"/dates/{DATE_3}")
    assert response4.status_code == status.HTTP_404_NOT_FOUND