import pytest
from datetime import datetime, date
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, conditional_seed
from app.db.models import UserUnavailablePeriod
from tests.utils.constants import BAD_ID_0000, USER_ID_1, USER_ID_2, EVENT_ID_1, EVENT_ID_3, USER_UNAVAILABLE_PERIOD_ID_1

# # =============================
# # INSERT USER UNAVAILABLE PERIOD
# # =============================
# @pytest.mark.parametrize("user_indices, date_indices, user_date_indices, payload, expected_status", [
#     # empty payload
#     ([], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields (date)
#     ([], [], [], {"user_id": USER_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields (user_id)
#     ([], [], [], {"date": DATE_2025_01_01}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid UUID format
#     ([], [], [], {"user_id": "invalid-uuid", "date": DATE_2025_01_01}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid date format
#     ([], [], [], {"user_id": USER_ID_1, "date": "invalid-date"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # duplicate user_date (index 0 = USER_ID_1 with DATE_2024_02_29)
#     ([0], [0, 1], [0], {"user_id": USER_ID_1, "date": DATE_2024_02_29}, status.HTTP_409_CONFLICT),
#     # extra fields not allowed
#     ([], [], [], {"user_id": USER_ID_1, "date": DATE_2025_01_01, "user_date_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # foreign key violation (user doesn't exist)
#     ([], [1], [], {"user_id": BAD_ID_0000, "date": DATE_2025_01_01}, status.HTTP_404_NOT_FOUND),
#     # foreign key violation (date doesn't exist)
#     ([0], [], [], {"user_id": USER_ID_1, "date": BAD_DATE_2000_01_01}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_insert_user_unavailable_period_error_cases(async_client, seed_dates, seed_users, seed_user_dates, test_users_data, test_dates_data, test_user_dates_data, user_indices, date_indices, user_date_indices, payload, expected_status):
#     """Test INSERT user unavailable period error cases (422, 409, and 404)"""
#     await conditional_seed(user_indices, test_users_data, seed_users)
#     await conditional_seed(date_indices, test_dates_data, seed_dates)
#     await conditional_seed(user_date_indices, test_user_dates_data, seed_user_dates)
    
#     response = await async_client.post("/user_unavailable_periods", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_insert_user_unavailable_period_success(async_client, seed_dates, seed_users, test_users_data, test_dates_data):
#     """Test valid user unavailable period insertion"""
#     await seed_users([test_users_data[1]])    
#     # Use DATE_2024_02_29 (index 0)
#     await seed_dates([test_dates_data[0]])
    
#     response = await async_client.post("/user_unavailable_periods", json={"user_id": USER_ID_2, "date": DATE_2024_02_29})
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert response_json["user_date_id"] is not None
#     assert response_json["user_id"] == USER_ID_2
#     assert response_json["date"] == DATE_2024_02_29

# # =============================
# # INSERT USER UNAVAILABLE PERIODS BULK
# # =============================
# @pytest.mark.parametrize("payload, expected_status", [
#     # empty list
#     ([], status.HTTP_400_BAD_REQUEST),
#     # missing required fields (date)
#     ([{"user_id": USER_ID_1}], status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields (user_id)
#     ([{"date": DATE_2024_02_29}], status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # extra fields not allowed
#     ([{"user_id": USER_ID_1, "date": DATE_2025_01_01, "is_active": "False"}], status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_insert_user_unavailable_periods_bulk_error_cases(async_client, payload, expected_status):
#     """Test INSERT user dates bulk error cases (400 and 422)"""
#     response = await async_client.post("/user_unavailable_periods/bulk", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_insert_user_unavailable_periods_bulk_success(async_client, seed_dates, seed_users, test_users_data, test_dates_data, test_user_dates_data):
#     """Test valid user dates bulk insertion"""
#     await seed_users(test_users_data[:2])
#     # Use first 3 dates (general dates)
#     await seed_dates(test_dates_data[:3])

#     good_payload = [test_user_dates_data[0], test_user_dates_data[1], test_user_dates_data[4]]

#     response = await async_client.post("/user_unavailable_periods/bulk", json=good_payload)
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert isinstance(response_json, list)
#     assert len(response_json) == 3
#     assert all(ud["user_date_id"] is not None for ud in response_json)
#     assert {ud["user_id"] for ud in response_json} == {USER_ID_1, USER_ID_2}
#     assert {ud["date"] for ud in response_json} == {DATE_2024_02_29, DATE_2025_01_01}

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
