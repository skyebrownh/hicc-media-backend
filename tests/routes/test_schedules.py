import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200
from tests.routes.conftest import conditional_seed, count_records
from tests.utils.constants import BAD_ID_0000, SCHEDULE_ID_1, SCHEDULE_ID_2, SCHEDULE_ID_3

# =============================
# GET ALL SCHEDULES
# =============================
@pytest.mark.asyncio
async def test_get_all_schedules_none_exist(async_client):
    """Test when no schedules exist returns empty list"""
    response = await async_client.get("/schedules")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedules_success(async_client, seed_schedules, test_schedules_data):
    """Test getting all schedules after inserting a variety"""
    seed_schedules(test_schedules_data)

    response = await async_client.get("/schedules")
    assert_list_200(response, expected_length=3)
    response_json = response.json()
    assert response_json[0]["month"] == 1
    assert response_json[0]["year"] == 2025
    assert response_json[1]["id"] is not None
    assert response_json[1]["month"] == 5
    assert response_json[1]["year"] == 2025
    assert response_json[1]["notes"] == "Second schedule"
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE SCHEDULE
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Schedule not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_schedule_error_cases(async_client, id, expected_status):
    """Test GET single schedule error cases (404 and 422)"""
    response = await async_client.get(f"/schedules/{id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_schedule_success(async_client, seed_schedules, test_schedules_data):
    """Test GET single schedule success case"""
    seed_schedules([test_schedules_data[0]])
    response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}")
    assert_single_item_200(response, expected_item={
        "id": SCHEDULE_ID_1,
        "month": 1,
        "year": 2025,
        "notes": "First schedule",
        "is_active": True
    })

# # =============================
# # GET ALL SCHEDULE DATES FOR SCHEDULE
# # =============================
# @pytest.mark.parametrize("schedule_id, expected_status", [
#     # Schedule not present
#     (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
#     # Invalid UUID format
#     ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_get_all_schedule_dates_for_schedule_error_cases(async_client, schedule_id, expected_status):
#     """Test GET all schedule dates for schedule error cases (404 and 422)"""
#     response = await async_client.get(f"/schedules/{schedule_id}/schedule_dates")
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_get_all_schedule_dates_for_schedule_none_exist(async_client, seed_dates, seed_schedules, seed_schedule_date_types, test_schedule_date_types_data, test_dates_data, test_schedules_data):
#     """Test when no schedule dates exist returns empty list"""
#     # Use DATE_2025_01_01 (index 1) for month_start_date
#     await seed_dates([test_dates_data[1]])
#     await seed_schedules([test_schedules_data[0]])
#     await seed_schedule_date_types(test_schedule_date_types_data)

#     response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
#     assert_empty_list_200(response)

# @pytest.mark.asyncio
# async def test_get_all_schedule_dates_for_schedule_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_schedule_date_types_data, test_dates_data, test_schedules_data, test_schedule_dates_data):
#     """Test getting all schedule dates for a schedule after inserting a variety"""
#     # Use DATE_2025_05_01 (index 3), DATE_2025_05_02 (index 4), DATE_2025_05_03 (index 5)
#     await seed_dates([test_dates_data[3], test_dates_data[4], test_dates_data[5]])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_schedule_date_types(test_schedule_date_types_data)
#     await seed_schedule_dates(test_schedule_dates_data)
    
#     response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}/schedule_dates")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, list)
#     assert len(response_json) == 3
#     assert response_json[0]["date"] == DATE_2025_05_01
#     assert response_json[1]["date"] == DATE_2025_05_02
#     assert response_json[2]["date"] == DATE_2025_05_03
#     assert response_json[1]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
#     assert response_json[1]["notes"] is None
#     assert response_json[2]["is_active"] is True

# # =============================
# # INSERT SCHEDULE
# # =============================
# @pytest.mark.parametrize("payload, expected_status", [
#     # empty payload
#     ({}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields
#     ({"notes": "missing required month_start_date"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid data types
#     ({"month_start_date": 12345, "notes": 999}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # schedule_id not allowed in payload
#     ({"schedule_id": "f8d3e340-9563-4de1-9146-675a8436242e", "month_start_date": DATE_2025_05_01}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # foreign key constraint violation
#     ({"month_start_date": BAD_DATE_2000_01_01}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_insert_schedule_error_cases(async_client, payload, expected_status):
#     """Test INSERT schedule error cases (422 and 404)"""
#     response = await async_client.post("/schedules", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_insert_schedule_success(async_client, seed_dates, test_dates_data):
#     """Test valid schedule insertion"""
#     # Use DATE_2025_05_01 (index 3) for month_start_date
#     await seed_dates([test_dates_data[3]])
    
#     response = await async_client.post("/schedules", json={
#         "month_start_date": DATE_2025_05_01,
#         "notes": "New schedule"
#     })
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert response_json["schedule_id"] is not None
#     assert response_json["month_start_date"] == DATE_2025_05_01
#     assert response_json["notes"] == "New schedule"
#     assert response_json["is_active"] is True

# # =============================
# # UPDATE SCHEDULE
# # =============================
# @pytest.mark.parametrize("schedule_path, payload, expected_status", [
#     # schedule not found
#     (f"/schedules/{BAD_ID_0000}", {"notes": "Updated schedule", "is_active": False}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ("/schedules/invalid-uuid-format", {"notes": "Updated schedule", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     (f"/schedules/{SCHEDULE_ID_3}", {}, status.HTTP_400_BAD_REQUEST),
#     # invalid data types
#     (f"/schedules/{SCHEDULE_ID_3}", {"month_start_date": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # non-updatable field
#     (f"/schedules/{SCHEDULE_ID_3}", {"schedule_id": SCHEDULE_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_update_schedule_error_cases(async_client, schedule_path, payload, expected_status):
#     """Test UPDATE schedule error cases (400, 404, and 422)"""
#     response = await async_client.patch(schedule_path, json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.parametrize("schedule_id, payload, expected_fields, unchanged_fields", [
#     # full update
#     (
#         SCHEDULE_ID_3,
#         {"notes": "Updated schedule", "is_active": False},
#         {"notes": "Updated schedule", "is_active": False},
#         {"month_start_date": DATE_2025_05_01}
#     ),
#     # partial update (is_active only)
#     (
#         SCHEDULE_ID_2,
#         {"is_active": False},
#         {"is_active": False},
#         {"month_start_date": DATE_2025_05_01}
#     ),
#     # partial update (notes only)
#     (
#         SCHEDULE_ID_1,
#         {"notes": "Partially Updated"},
#         {"notes": "Partially Updated"},
#         {"month_start_date": DATE_2025_01_01, "is_active": True}
#     ),
# ])
# @pytest.mark.asyncio
# async def test_update_schedule_success(async_client, seed_dates, seed_schedules, test_schedules_data, test_dates_data, schedule_id, payload, expected_fields, unchanged_fields):
#     """Test valid schedule updates"""
#     # Use DATE_2025_01_01 (index 1), DATE_2025_05_01 (index 3)
#     await seed_dates([test_dates_data[1], test_dates_data[3]])
#     await seed_schedules(test_schedules_data)
    
#     response = await async_client.patch(f"/schedules/{schedule_id}", json=payload)
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     for field, expected_value in expected_fields.items():
#         assert response_json[field] == expected_value
#     for field, expected_value in unchanged_fields.items():
#         assert response_json[field] == expected_value

# # =============================
# # DELETE SCHEDULE
# # =============================
# @pytest.mark.parametrize("schedule_path, expected_status", [
#     # schedule not found
#     (f"/schedules/{BAD_ID_0000}", status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ("/schedules/invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_delete_schedule_error_cases(async_client, schedule_path, expected_status):
#     """Test DELETE schedule error cases (404 and 422)"""
#     response = await async_client.delete(schedule_path)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_delete_schedule_success(async_client, seed_dates, seed_schedules, test_schedules_data, test_dates_data):
#     """Test successful schedule deletion"""
#     # Use DATE_2025_05_01 (index 3)
#     await seed_dates([test_dates_data[3]])
#     await seed_schedules([test_schedules_data[1]])

#     response = await async_client.delete(f"/schedules/{SCHEDULE_ID_2}")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, dict)
#     assert response_json["month_start_date"] == DATE_2025_05_01
#     assert response_json["schedule_id"] == SCHEDULE_ID_2

# # =============================
# # DELETE SCHEDULE DATES FOR SCHEDULE
# # =============================
# @pytest.mark.parametrize("schedule_id, expected_status", [
#     # Schedule not present
#     (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
#     # Invalid UUID format
#     ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_delete_schedule_dates_for_schedule_error_cases(async_client, schedule_id, expected_status):
#     """Test DELETE schedule dates for schedule error cases (404 and 422)"""
#     response = await async_client.delete(f"/schedules/{schedule_id}/schedule_dates")
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_delete_schedule_dates_for_schedule_none_exist(async_client, seed_dates, seed_schedules, test_dates_data, test_schedules_data):
#     """Test DELETE schedule dates for schedule when none exist returns empty list"""
#     # Use DATE_2025_01_01 (index 1) for month_start_date
#     await seed_dates([test_dates_data[1]])
#     await seed_schedules([test_schedules_data[0]])

#     response = await async_client.delete(f"/schedules/{SCHEDULE_ID_1}/schedule_dates")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, list)
#     assert len(response_json) == 0
#     assert response_json == []

# @pytest.mark.asyncio
# async def test_delete_schedule_dates_for_schedule_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, test_schedule_date_types_data, test_dates_data, test_schedules_data, test_schedule_dates_data):
#     """Test successful deletion of all schedule dates for a schedule when schedule dates exist"""
#     # Use DATE_2025_05_01 (index 3) for month_start_date
#     await seed_dates([test_dates_data[3], test_dates_data[4], test_dates_data[5]])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_schedule_date_types(test_schedule_date_types_data)
#     await seed_schedule_dates(test_schedule_dates_data)

#     response = await async_client.delete(f"/schedules/{SCHEDULE_ID_2}/schedule_dates")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, list)
#     assert len(response_json) == 3
#     assert response_json[0]["date"] == DATE_2025_05_01
#     assert response_json[0]["schedule_date_type_id"] == SCHEDULE_DATE_TYPE_ID_1
#     assert response_json[1]["date"] == DATE_2025_05_02
#     assert response_json[2]["date"] == DATE_2025_05_03

#     # Verify deletion by trying to get it again
#     verify_response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}/schedule_dates")
#     assert_empty_list_200(verify_response)

# # =============================
# # DELETE SCHEDULE CASCADE
# # =============================
# @pytest.mark.parametrize("date_indices, schedule_date_type_indices, schedule_date_indices, expected_count_before", [
#     # No schedule_dates to cascade delete (only month_start_date at index 1)
#     ([], [], [], 0),
#     # One schedule_date to cascade delete (month_start_date + one schedule_date at index 3)
#     ([], [0], [0], 1),
#     # Multiple schedule_dates to cascade delete (month_start_date + schedule_dates at indices 3, 4, 5)
#     ([3, 4, 5], [0], [0, 1, 2], 3),
# ])
# @pytest.mark.asyncio
# async def test_delete_schedule_cascade_schedule_dates(
#     async_client, test_db_pool, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates,
#     test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data,
#     date_indices, schedule_date_type_indices, schedule_date_indices, expected_count_before
# ):
#     """Test that deleting a schedule cascades to delete associated schedule_dates"""
#     # Seed dates first (schedule needs month_start_date to exist)
#     # Always seed the schedule's month_start_date (DATE_2025_05_01 at index 3)
#     schedule_month_start_date = test_dates_data[3]
#     await seed_dates([schedule_month_start_date])
    
#     # Seed parent
#     await seed_schedules([test_schedules_data[1]])

#     # Seed child records based on parameters
#     # Add any additional dates needed for schedule_dates
#     additional_dates = [test_dates_data[i] for i in date_indices if test_dates_data[i] != schedule_month_start_date]
#     if additional_dates:
#         await seed_dates(additional_dates)
#     await conditional_seed(schedule_date_type_indices, test_schedule_date_types_data, seed_schedule_date_types)
#     await conditional_seed(schedule_date_indices, test_schedule_dates_data, seed_schedule_dates)

#     # Verify schedule_dates exist before deletion
#     count_before = await count_records(test_db_pool, "schedule_dates", f"schedule_id = '{SCHEDULE_ID_2}'")
#     assert count_before == expected_count_before

#     # Delete parent
#     response = await async_client.delete(f"/schedules/{SCHEDULE_ID_2}")
#     assert response.status_code == status.HTTP_200_OK

#     # Verify parent is deleted
#     verify_response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}")
#     assert verify_response.status_code == status.HTTP_404_NOT_FOUND

#     # Verify all child records are cascade deleted
#     count_after = await count_records(test_db_pool, "schedule_dates", f"schedule_id = '{SCHEDULE_ID_2}'")
#     assert count_after == 0

# @pytest.mark.parametrize("schedule_date_indices, media_role_indices, schedule_date_role_indices, expected_schedule_date_count, expected_schedule_date_role_count", [
#     # No schedule_dates, so no schedule_date_roles
#     ([], [], [], 0, 0),
#     # One schedule_date with one schedule_date_role
#     ([0], [0], [0], 1, 1),
#     # One schedule_date with multiple schedule_date_roles
#     ([0], [0, 1], [0, 1], 1, 2),
#     # Multiple schedule_dates with multiple schedule_date_roles
#     ([0, 1], [0, 1], [0, 1, 2], 2, 3),
# ])
# @pytest.mark.asyncio
# async def test_delete_schedule_cascade_multi_level(
#     async_client, test_db_pool, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates,
#     seed_media_roles, seed_schedule_date_roles, seed_users, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data,
#     test_media_roles_data, test_schedule_date_roles_data, test_users_data, test_dates_data,
#     schedule_date_indices, media_role_indices, schedule_date_role_indices,
#     expected_schedule_date_count, expected_schedule_date_role_count
# ):
#     """Test that deleting a schedule cascades through multiple levels: schedule -> schedule_dates -> schedule_date_roles"""
#     # Always seed the schedule's month_start_date (DATE_2025_05_01 at index 3)
#     schedule_month_start_date = test_dates_data[3]
#     await seed_dates([schedule_month_start_date])
    
#     # Seed parent
#     await seed_schedules([test_schedules_data[1]])

#     # Seed schedule_date_types (required for schedule_dates)
#     await seed_schedule_date_types(test_schedule_date_types_data)

#     # Seed dates needed for schedule_dates (excluding schedule_month_start_date which is already seeded)
#     if schedule_date_indices:
#         schedule_dates_to_seed = [test_schedule_dates_data[i] for i in schedule_date_indices]
#         dates_needed = {sd["date"] for sd in schedule_dates_to_seed}
#         dates_needed.discard(schedule_month_start_date)  # Remove if present since already seeded
#         if dates_needed:
#             await seed_dates(list(dates_needed))

#     # Seed schedule_dates based on parameters
#     await conditional_seed(schedule_date_indices, test_schedule_dates_data, seed_schedule_dates)

#     # Seed users if any schedule_date_roles have assigned_user_id
#     if schedule_date_role_indices:
#         user_ids_needed = {test_schedule_date_roles_data[i].get("assigned_user_id") for i in schedule_date_role_indices if test_schedule_date_roles_data[i].get("assigned_user_id")}
#         if user_ids_needed:
#             await seed_users([test_users_data[0]])

#     # Seed media_roles (required for schedule_date_roles)
#     await conditional_seed(media_role_indices, test_media_roles_data, seed_media_roles)

#     # Seed schedule_date_roles based on parameters
#     await conditional_seed(schedule_date_role_indices, test_schedule_date_roles_data, seed_schedule_date_roles)

#     # Get the schedule_date_ids that will be created for verification
#     schedule_date_ids = []
#     if schedule_date_indices:
#         schedule_date_ids = [test_schedule_dates_data[i]["schedule_date_id"] for i in schedule_date_indices]

#     # Verify records exist before deletion
#     schedule_date_count_before = await count_records(test_db_pool, "schedule_dates", f"schedule_id = '{SCHEDULE_ID_2}'")
#     if schedule_date_ids:
#         schedule_date_ids_str = "', '".join(schedule_date_ids)
#         schedule_date_role_count_before = await count_records(test_db_pool, "schedule_date_roles", f"schedule_date_id IN ('{schedule_date_ids_str}')")
#     else:
#         schedule_date_role_count_before = 0
#     assert schedule_date_count_before == expected_schedule_date_count
#     assert schedule_date_role_count_before == expected_schedule_date_role_count

#     # Delete parent schedule
#     response = await async_client.delete(f"/schedules/{SCHEDULE_ID_2}")
#     assert response.status_code == status.HTTP_200_OK

#     # Verify parent is deleted
#     verify_response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}")
#     assert verify_response.status_code == status.HTTP_404_NOT_FOUND

#     # Verify all schedule_dates are cascade deleted (first level)
#     schedule_date_count_after = await count_records(test_db_pool, "schedule_dates", f"schedule_id = '{SCHEDULE_ID_2}'")
#     assert schedule_date_count_after == 0

#     # Verify all schedule_date_roles are cascade deleted (second level - through schedule_dates)
#     # Check using the specific schedule_date_ids we know were created
#     if schedule_date_ids:
#         schedule_date_ids_str = "', '".join(schedule_date_ids)
#         schedule_date_role_count_after = await count_records(test_db_pool, "schedule_date_roles", f"schedule_date_id IN ('{schedule_date_ids_str}')")
#     else:
#         schedule_date_role_count_after = 0
#     assert schedule_date_role_count_after == 0
