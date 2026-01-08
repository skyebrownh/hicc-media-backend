import pytest
from datetime import datetime, date
from fastapi import status
from tests.utils.helpers import assert_single_item_201, assert_list_201, conditional_seed, parse_to_utc
from app.db.models import UserUnavailablePeriod
from tests.utils.constants import BAD_ID_0000, DATETIME_2025_01_01, DATETIME_2025_01_02, DATETIME_2025_05_01, DATETIME_2025_05_02, USER_ID_1, USER_ID_2, EVENT_ID_1, EVENT_ID_3, USER_UNAVAILABLE_PERIOD_ID_1

STARTS_AT = DATETIME_2025_01_01.isoformat()
ENDS_AT = DATETIME_2025_01_02.isoformat()
STARTS_AT_2 = DATETIME_2025_05_01.isoformat()
ENDS_AT_2 = DATETIME_2025_05_02.isoformat()
VALID_PAYLOAD = {"starts_at": STARTS_AT, "ends_at": ENDS_AT}
VALID_PAYLOAD_2 = {"starts_at": STARTS_AT_2, "ends_at": ENDS_AT_2}

# =============================
# INSERT USER UNAVAILABLE PERIOD
# =============================
@pytest.mark.parametrize("user_indices, user_id, payload, expected_status", [
    ([], BAD_ID_0000, VALID_PAYLOAD, status.HTTP_404_NOT_FOUND), # user not found
    ([], USER_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    ([], USER_ID_1, {"starts_at": STARTS_AT}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields (ends_at)
    ([], USER_ID_1, {"starts_at": "invalid-datetime", "ends_at": ENDS_AT}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid format in payload
    ([0], USER_ID_1, {"starts_at": ENDS_AT, "ends_at": STARTS_AT}, status.HTTP_422_UNPROCESSABLE_CONTENT), # violates check constraint
    ([], USER_ID_1, {"id": BAD_ID_0000, **VALID_PAYLOAD}, status.HTTP_422_UNPROCESSABLE_CONTENT), # extra fields not allowed
])
@pytest.mark.asyncio
async def test_insert_user_unavailable_period_error_cases(async_client, seed_users, test_users_data, user_indices, user_id, payload, expected_status):
    """Test INSERT user unavailable period error cases (400, 404, 422, and 409)"""
    conditional_seed(user_indices, test_users_data, seed_users)
    response = await async_client.post(f"/users/{user_id}/availability", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_user_unavailable_period_success(async_client, seed_users, test_users_data):
    """Test valid user unavailable period insertion"""
    seed_users([test_users_data[0]])    
    response = await async_client.post(f"/users/{USER_ID_1}/availability", json=VALID_PAYLOAD)
    response_json = response.json()
    assert parse_to_utc(response_json["starts_at"]) == DATETIME_2025_01_01
    assert parse_to_utc(response_json["ends_at"]) == DATETIME_2025_01_02
    assert_single_item_201(response, expected_item={
        "user_id": USER_ID_1,
        "user_first_name": "Alice",
        "user_last_name": "Smith",
        "user_email": "alice@example.com",
        "user_phone": "555-1111",
        "user_is_active": True
    })

# =============================
# INSERT USER UNAVAILABLE PERIODS BULK
# =============================
@pytest.mark.parametrize("user_indices, user_id, payload, expected_status", [
    ([], BAD_ID_0000, [VALID_PAYLOAD], status.HTTP_404_NOT_FOUND), # user not found
    ([0], USER_ID_1, [], status.HTTP_400_BAD_REQUEST), # empty list
    ([], USER_ID_1, [{"starts_at": STARTS_AT}], status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields (ends_at)
    ([], USER_ID_1, [{"starts_at": "invalid-datetime", "ends_at": ENDS_AT}], status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid format in payload
    ([0], USER_ID_1, [{"starts_at": ENDS_AT, "ends_at": STARTS_AT}], status.HTTP_422_UNPROCESSABLE_CONTENT), # violates check constraint
    ([], USER_ID_1, [{"id": BAD_ID_0000, **VALID_PAYLOAD}], status.HTTP_422_UNPROCESSABLE_CONTENT), # extra fields not allowed
])
@pytest.mark.asyncio
async def test_insert_user_unavailable_periods_bulk_error_cases(async_client, seed_users, test_users_data, user_indices, user_id, payload, expected_status):
    conditional_seed(user_indices, test_users_data, seed_users)
    """Test INSERT user unavailable periods bulk error cases (400, 404, and 422)"""
    response = await async_client.post(f"/users/{user_id}/availability/bulk", json=payload)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insert_user_unavailable_periods_bulk_success(async_client, seed_users, test_users_data):
    """Test valid user dates bulk insertion"""
    seed_users([test_users_data[0]])
    response = await async_client.post(f"/users/{USER_ID_1}/availability/bulk", json=[VALID_PAYLOAD, VALID_PAYLOAD_2])
    response_json = response.json()
    assert_list_201(response, expected_length=2)

    # shape assertions
    for item in response_json:
        assert "id" in item
        assert "user_id" in item
        assert "user_first_name" in item
        assert "starts_at" in item
        assert "ends_at" in item
    
    # data assertions
    assert all(item["user_id"] == USER_ID_1 for item in response_json)
    assert response_json[0]["id"] is not None
    assert response_json[0]["user_first_name"] == "Alice"
    assert parse_to_utc(response_json[0]["starts_at"]) == DATETIME_2025_01_01
    assert parse_to_utc(response_json[0]["ends_at"]) == DATETIME_2025_01_02
    assert response_json[1]["user_email"] == "alice@example.com"
    assert parse_to_utc(response_json[1]["starts_at"]) == DATETIME_2025_05_01
    assert parse_to_utc(response_json[1]["ends_at"]) == DATETIME_2025_05_02

# # =============================
# # UPDATE USER UNAVAILABLE PERIOD
# # =============================
# @pytest.mark.parametrize("user_id, date_path, payload, expected_status", [
#     # user date not found
#     (USER_ID_1, f"/users/{USER_ID_1}/dates/{DATE_2025_01_01}", {"date": DATE_2025_01_01}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format for user_id
#     ("invalid-uuid-format", f"/users/invalid-uuid-format/dates/{DATE_2024_02_29}", {"date": DATE_2025_01_01}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid date format in path
#     (USER_ID_1, f"/users/{USER_ID_1}/dates/invalid-date-format", {"date": DATE_2025_01_01}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     (USER_ID_1, f"/users/{USER_ID_1}/dates/{DATE_2024_02_29}", {}, status.HTTP_400_BAD_REQUEST),
#     # invalid date format in payload
#     (USER_ID_1, f"/users/{USER_ID_1}/dates/{DATE_2024_02_29}", {"date": "invalid-date"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # foreign key violation (date doesn't exist)
#     (USER_ID_1, f"/users/{USER_ID_1}/dates/{DATE_2025_01_01}", {"date": BAD_DATE_2000_01_01}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_update_user_unavailable_period_error_cases(async_client, user_id, date_path, payload, expected_status):
#     """Test UPDATE user date error cases (400, 404, and 422)"""
#     response = await async_client.patch(date_path, json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_update_user_unavailable_period_success(async_client, seed_dates, seed_users, seed_user_dates, test_users_data, test_dates_data, test_user_dates_data):
#     """Test valid user date update"""
#     await seed_users([test_users_data[0]])    
#     # Use first 2 dates (DATE_2024_02_29, DATE_2025_01_01)
#     await seed_dates(test_dates_data[:2])
#     await seed_user_dates([test_user_dates_data[0]])

#     response = await async_client.patch(f"/users/{USER_ID_1}/dates/{DATE_2024_02_29}", json={"date": DATE_2025_01_01})
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert response_json["user_id"] == USER_ID_1
#     assert response_json["date"] == DATE_2025_01_01

# =============================
# DELETE USER UNAVAILABLE PERIOD
# =============================
@pytest.mark.asyncio
async def test_delete_user_unavailable_period_error_cases(async_client):
    """Test DELETE user unavailable period error cases (400)"""
    response = await async_client.delete("/user_availability/invalid-uuid-format")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_delete_user_unavailable_period_success(async_client, get_test_db_session, seed_user_unavailable_periods, seed_users, test_user_unavailable_periods_data, test_users_data):
    """Test successful user unavailable period deletion with verification"""
    seed_users([test_users_data[0]])
    seed_user_unavailable_periods([test_user_unavailable_periods_data[0]])
    response = await async_client.delete(f"/user_availability/{USER_UNAVAILABLE_PERIOD_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to query it directly
    verify_response = get_test_db_session.get(UserUnavailablePeriod, USER_UNAVAILABLE_PERIOD_ID_1)
    assert verify_response is None

    # Verify valid user unavailable period id that does not exist returns 204
    verify_response2 = await async_client.delete(f"/user_availability/{BAD_ID_0000}")
    assert verify_response2.status_code == status.HTTP_204_NO_CONTENT
