import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import DATE_2024_02_29, DATE_2025_01_01, DATE_2025_03_31, DATE_2025_08_31, DATE_2025_12_31

# =============================
# GET ALL DATES
# =============================
@pytest.mark.asyncio
async def test_get_all_dates_none_exist(async_client):
    """Test when no dates exist returns empty list"""
    response = await async_client.get("/dates")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_dates_success(async_client, seed_dates, test_dates_data):
    """Test getting all dates after inserting a variety, asserts on correct date columns per-date"""
    # Use first 2 dates + last 2 dates (general dates: first of year, leap day, end of year, 5th Sunday of August)
    general_dates = test_dates_data[:2] + test_dates_data[-2:]
    await seed_dates(general_dates)

    response = await async_client.get("/dates")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    returned_dates = [d["date"] for d in response_json]
    for d in general_dates:
        assert d in returned_dates
    assert len(response_json) == len(general_dates) 

    for row in response_json:
        d = row["date"]
        if d == DATE_2025_01_01:  # first of year/month
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
        elif d == DATE_2024_02_29:  # leap year, last day Feb
            assert row["is_last_of_month"] is True
            assert row["calendar_day"] == 29
        elif d == DATE_2025_12_31:  # last of year/month
            assert row["is_last_of_month"] is True
        elif d == DATE_2025_08_31:  # 5th Sunday of August
            assert row["is_last_of_month"] is True
            assert row["weekday_of_month"] == 5
            assert row["calendar_quarter"] == 3
            assert row["weekday"] == 6 # Sunday

# =============================
# GET SINGLE DATE
# =============================
@pytest.mark.parametrize("date_indices, query_date, expected_status", [
    ([], DATE_2025_01_01, status.HTTP_404_NOT_FOUND),
    ([], "invalid-date-format", status.HTTP_422_UNPROCESSABLE_CONTENT),  # Invalid date format
])
@pytest.mark.asyncio
async def test_get_single_date_error_cases(async_client, seed_dates, test_dates_data, date_indices, query_date, expected_status):
    """Test GET single date error cases (404 and 422)"""
    await conditional_seed(date_indices, test_dates_data, seed_dates)
    response = await async_client.get(f"/dates/{query_date}")
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_get_single_date_success(async_client, seed_dates, test_dates_data):
    """Test GET single date success case"""
    # Use DATE_2025_03_31 (index 2)
    await seed_dates([test_dates_data[2]])
    response = await async_client.get(f"/dates/{DATE_2025_03_31}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert data["date"] == DATE_2025_03_31

# =============================
# INSERT DATE
# =============================
@pytest.mark.parametrize("date_indices, payload, expected_status", [
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),  # empty payload
    ([], {"date": "invalid-date"}, status.HTTP_422_UNPROCESSABLE_CONTENT),  # invalid date format
    ([], {"date": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),  # invalid data type
    ([], {"date": DATE_2025_08_31, "calendar_year": 2025}, status.HTTP_422_UNPROCESSABLE_CONTENT),  # extra fields not allowed
    ([2], {"date": DATE_2025_03_31}, status.HTTP_409_CONFLICT),  # duplicate date (index 2 = DATE_2025_03_31)
])
@pytest.mark.asyncio
async def test_insert_date_error_cases(async_client, seed_dates, test_dates_data, date_indices, payload, expected_status):
    """Test INSERT date error cases (422 and 409)"""
    await conditional_seed(date_indices, test_dates_data, seed_dates)
    
    response = await async_client.post("/dates", json=payload)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_insert_date_success(async_client):
    """Test valid date insertion"""
    response = await async_client.post("/dates", json={"date": DATE_2025_08_31})
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["date"] == DATE_2025_08_31
    assert response_json["calendar_month"] == 8
    assert response_json["calendar_day"] == 31
    # Check that auto-generated fields exist
    assert "is_weekend" in response_json
    assert "is_weekday" in response_json
    assert "weekday" in response_json

# =============================
# UPDATE DATE
# =============================
@pytest.mark.parametrize("date_indices, date_path, payload, expected_status", [
    # date not found
    ([1], f"/dates/{DATE_2025_12_31}", {"is_holiday": True}, status.HTTP_404_NOT_FOUND),
    # invalid date format in path
    ([2], "/dates/invalid-date-format", {"is_holiday": True}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid data type in payload
    ([2], f"/dates/{DATE_2025_03_31}", {"calendar_year": "invalid"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # empty payload
    ([2], f"/dates/{DATE_2025_03_31}", {}, status.HTTP_400_BAD_REQUEST),
])
@pytest.mark.asyncio
async def test_update_date_error_cases(async_client, seed_dates, test_dates_data, date_indices, date_path, payload, expected_status):
    """Test UPDATE date error cases (400, 404, and 422)"""
    await conditional_seed(date_indices, test_dates_data, seed_dates)
    
    response = await async_client.patch(date_path, json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize("date, payload, expected_fields, unchanged_fields", [
    (DATE_2025_03_31, {"is_holiday": True, "is_weekend": False}, {"is_holiday": True, "is_weekend": False}, {}),
    (DATE_2025_01_01, {"is_holiday": True}, {"is_holiday": True}, {"calendar_year": 2025}),
    (DATE_2025_01_01, {"calendar_year": 2026}, {"calendar_year": 2026}, {}),
])
@pytest.mark.asyncio
async def test_update_date_success(async_client, seed_dates, test_dates_data, date, payload, expected_fields, unchanged_fields):
    """Test valid date updates"""
    # Use DATE_2025_01_01 and DATE_2025_03_31 (indices 1 and 2)
    await seed_dates(test_dates_data[1:3])
    
    response = await async_client.patch(f"/dates/{date}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value
    for field, expected_value in unchanged_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE DATE
# =============================
@pytest.mark.parametrize("date_path, expected_status", [
    # date not found
    (f"/dates/{DATE_2025_12_31}", status.HTTP_404_NOT_FOUND),
    # invalid date format in path
    ("/dates/invalid-date-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_delete_date_error_cases(async_client, date_path, expected_status):
    """Test DELETE date error cases (404 and 422)"""
    response = await async_client.delete(date_path)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_delete_date_success(async_client, seed_dates, test_dates_data):
    """Test successful date deletion with verification"""
    # Use DATE_2025_03_31 (index 2)
    await seed_dates([test_dates_data[2]])

    # Test successful deletion
    response = await async_client.delete(f"/dates/{DATE_2025_03_31}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["date"] == DATE_2025_03_31

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/dates/{DATE_2025_03_31}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND