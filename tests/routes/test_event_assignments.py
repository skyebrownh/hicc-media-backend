import pytest
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200
from tests.routes.conftest import conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, EVENT_ID_1, EVENT_ID_2, ROLE_ID_1, ROLE_ID_2, ROLE_ID_3,
    USER_ID_1, USER_ID_2, EVENT_ASSIGNMENT_ID_1, EVENT_ASSIGNMENT_ID_2, SCHEDULE_ID_2
)

# =============================
# GET ALL EVENT ASSIGNMENTS
# =============================
@pytest.mark.asyncio
async def test_get_all_event_assignments_none_exist(async_client):
    """Test GET all event assignments when none exist"""
    response = await async_client.get("/event_assignments")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_event_assignments_success(async_client, seed_roles, seed_proficiency_levels, seed_users, seed_user_roles, seed_schedules, seed_event_types, seed_events, seed_event_assignments, test_roles_data, test_proficiency_levels_data, test_users_data, test_user_roles_data, test_schedules_data, test_event_types_data, test_events_data, test_event_assignments_data):
    """Test GET all event assignments success case"""
    seed_roles(test_roles_data[:2])
    seed_proficiency_levels([test_proficiency_levels_data[0]])
    seed_users([test_users_data[0]])
    seed_user_roles([test_user_roles_data[0]])
    seed_schedules([test_schedules_data[1]])
    seed_event_types([test_event_types_data[0]])
    seed_events(test_events_data[:2])
    seed_event_assignments(test_event_assignments_data)

    response = await async_client.get("/event_assignments")
    assert_list_200(response, expected_length=3)
    response_json = response.json()

    # shape assertions
    assert all("id" in ea for ea in response_json)
    assert all("event_id" in ea for ea in response_json)
    assert all("role_id" in ea for ea in response_json)
    assert all("is_applicable" in ea for ea in response_json)
    assert all("requirement_level" in ea for ea in response_json)
    assert all("assigned_user_id" in ea for ea in response_json)
    assert all("event_starts_at" in ea for ea in response_json)
    assert all("event_schedule_year" in ea for ea in response_json)
    assert all("event_team_code" in ea for ea in response_json)
    assert all("event_type_name" in ea for ea in response_json)
    assert all("role_code" in ea for ea in response_json)
    assert all("assigned_user_phone" in ea for ea in response_json)
    assert all("proficiency_level_name" in ea for ea in response_json)

    # data assertions
    assert response_json[0]["id"] is not None
    assert response_json[0]["event_id"] == EVENT_ID_1
    assert response_json[0]["role_id"] == ROLE_ID_1
    assert response_json[0]["assigned_user_id"] == USER_ID_1
    assert response_json[0]["proficiency_level_rank"] == 3
    assert response_json[1]["is_applicable"] is True
    assert response_json[1]["requirement_level"] == "REQUIRED"
    assert response_json[1]["assigned_user_phone"] is None
    assert response_json[1]["event_schedule_id"] == SCHEDULE_ID_2
    assert response_json[1]["event_team_name"] is None
    assert response_json[2]["event_type_code"] == "service"
    assert response_json[2]["role_code"] == "propresenter"

# # =============================
# # GET SINGLE EVENT ASSIGNMENT
# # =============================
# @pytest.mark.parametrize("event_assignment_id, expected_status", [
#     # Event assignment not found
#     (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
#     # Invalid UUID format
#     ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_get_single_event_assignment_error_cases(async_client, event_assignment_id, expected_status):
#     """Test GET single schedule date role error cases (404 and 422)"""
#     response = await async_client.get(f"/event_assignments/{event_assignment_id}")
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_get_single_event_assignment_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, seed_users, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data, test_users_data):
#     """Test GET single event assignment success case"""
#     # DATE_2025_05_01 (index 3) for schedule_date
#     await seed_dates([test_dates_data[3]])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_schedule_date_types([test_schedule_date_types_data[0]])
#     await seed_schedule_dates([test_schedule_dates_data[0]])
#     await seed_users([test_users_data[0]])
#     await seed_media_roles([test_media_roles_data[0]])
#     await seed_schedule_date_roles([test_schedule_date_roles_data[0]])
    
#     response = await async_client.get(f"/event_assignments/{EVENT_ASSIGNMENT_ID_1}")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, dict)
#     assert response_json["event_assignment_id"] == EVENT_ASSIGNMENT_ID_1
#     assert response_json["schedule_date_id"] == SCHEDULE_DATE_ID_1
#     assert response_json["media_role_id"] == MEDIA_ROLE_ID_1
#     assert response_json["assigned_user_id"] == USER_ID_1
#     assert response_json["is_required"] is True
#     assert response_json["is_preferred"] is False
#     assert response_json["is_active"] is True

# # =============================
# # INSERT EVENT ASSIGNMENT
# # =============================
# @pytest.mark.parametrize("date_indices, schedule_indices, type_indices, schedule_date_indices, media_role_indices, schedule_date_role_indices, payload, expected_status", [
#     # Empty payload
#     ([], [], [], [], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # Missing required fields (event_id)
#     ([], [], [], [], [], [], {"role_id": ROLE_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # Missing required fields (role_id)
#     ([], [], [], [], [], [], {"event_id": EVENT_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # Invalid UUID format
#     ([], [], [], [], [], [], {"event_id": "invalid-uuid", "role_id": ROLE_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # Extra fields not allowed
#     ([], [], [], [], [], [], {"event_id": EVENT_ID_1, "role_id": ROLE_ID_2, "event_assignment_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # Duplicate event assignment (event_index 1 = second event)
#     # Seed event assignment on EVENT_ID_2, then try to insert duplicate
#     ([1, 2], [1], [0], [1], [0], [2], {"event_id": EVENT_ID_2, "role_id": ROLE_ID_1}, status.HTTP_409_CONFLICT),
#     # Foreign key violation (event doesn't exist)
#     ([], [], [], [], [1], [], {"event_id": BAD_ID_0000, "role_id": ROLE_ID_2}, status.HTTP_404_NOT_FOUND),
#     # Foreign key violation (role doesn't exist)
#     ([1], [1], [0], [0], [], [], {"event_id": EVENT_ID_1, "role_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
#     # Foreign key violation (user doesn't exist)
#     ([1], [1], [0], [0], [1], [], {"event_id": EVENT_ID_1, "role_id": ROLE_ID_2, "assigned_user_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_insert_event_assignment_error_cases(
#     async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates,
#     seed_media_roles, seed_schedule_date_roles, test_dates_data, test_schedules_data,
#     test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data,
#     date_indices, schedule_indices, type_indices, schedule_date_indices, media_role_indices,
#     schedule_date_role_indices, payload, expected_status
# ):
#     """Test INSERT event assignment error cases (422, 409, and 404)"""
#     # Collect all dates needed
#     all_dates_needed = set()
#     # Dates from date_indices
#     if date_indices:
#         all_dates_needed.update([test_dates_data[i] for i in date_indices])
#     # Dates needed for schedules' month_start_date
#     if schedule_indices:
#         all_dates_needed.update([test_schedules_data[i]["month_start_date"] for i in schedule_indices])
#     # Dates needed for schedule_dates
#     if schedule_date_indices:
#         all_dates_needed.update([test_schedule_dates_data[i]["date"] for i in schedule_date_indices])
#     # Seed all dates at once
#     if all_dates_needed:
#         await seed_dates(list(all_dates_needed))
    
#     await conditional_seed(schedule_indices, test_schedules_data, seed_schedules)
#     await conditional_seed(type_indices, test_schedule_date_types_data, seed_schedule_date_types)
#     await conditional_seed(schedule_date_indices, test_schedule_dates_data, seed_schedule_dates)
#     await conditional_seed(media_role_indices, test_media_roles_data, seed_media_roles)
#     await conditional_seed(schedule_date_role_indices, test_schedule_date_roles_data, seed_schedule_date_roles)
    
#     response = await async_client.post("/event_assignments", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.parametrize("payload, expected_fields", [
#     # Basic insert
#     (
#         {"event_id": EVENT_ID_1, "role_id": ROLE_ID_2},
#         {"event_id": EVENT_ID_1, "role_id": ROLE_ID_2, "is_applicable": False, "requirement_level": "PREFERRED", "assigned_user_id": USER_ID_2, "is_active": True}
#     ),
#     # Insert with optional fields
#     (
#         {"event_id": EVENT_ID_2, "role_id": ROLE_ID_1, "assigned_user_id": USER_ID_2, "is_applicable": False, "requirement_level": "OPTIONAL", "is_active": True},
#         {"event_id": EVENT_ID_2, "role_id": ROLE_ID_1, "assigned_user_id": USER_ID_2, "is_applicable": False, "requirement_level": "OPTIONAL", "is_active": True}
#     ),
# ])
# @pytest.mark.asyncio
# async def test_insert_event_assignment_success(async_client, seed_dates, seed_users, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, test_dates_data, test_users_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, payload, expected_fields):
#     """Test INSERT event assignment success cases"""
#     # DATE_2025_05_01/02 (indices 3,4) for schedule_dates
#     await seed_dates([test_dates_data[3], test_dates_data[4]])
#     await seed_users(test_users_data[:2])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_schedule_date_types([test_schedule_date_types_data[0]])
#     await seed_schedule_dates(test_schedule_dates_data[:2])
#     await seed_media_roles(test_media_roles_data[:3])

#     response = await async_client.post("/event_assignments", json=payload)
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert response_json["event_assignment_id"] is not None
#     for field, expected_value in expected_fields.items():
#         assert response_json[field] == expected_value

# # =============================
# # UPDATE EVENT ASSIGNMENT
# # =============================
# @pytest.mark.parametrize("event_assignment_id, payload, expected_status", [
#     # Event assignment not found
#     (BAD_ID_0000, {"assigned_user_id": USER_ID_2}, status.HTTP_404_NOT_FOUND),
#     # Invalid UUID format
#     ("invalid-uuid-format", {"assigned_user_id": USER_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # Empty payload
#     (EVENT_ASSIGNMENT_ID_1, {}, status.HTTP_400_BAD_REQUEST),
#     # Foreign key violation (user doesn't exist)
#     (EVENT_ASSIGNMENT_ID_1, {"assigned_user_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_update_event_assignment_error_cases(async_client, seed_users, test_users_data, event_assignment_id, payload, expected_status):
#     """Test UPDATE event assignment error cases (400, 404, and 422)"""
#     await seed_users([test_users_data[1]])
    
#     response = await async_client.patch(f"/event_assignments/{event_assignment_id}", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.parametrize("payload, expected_fields", [
#     # Update assigned_user_id
#     ({"assigned_user_id": USER_ID_2}, {"assigned_user_id": USER_ID_2}),
#     # Update is_required
#     ({"is_required": False}, {"is_required": False}),
#     # Update is_preferred
#     ({"is_preferred": True}, {"is_preferred": True}),
#     # Update is_active
#     ({"is_active": False}, {"is_active": False}),
# ])
# @pytest.mark.asyncio
# async def test_update_event_assignment_success(async_client, seed_dates, seed_users, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_users_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data, payload, expected_fields):
#     """Test UPDATE event assignment success cases"""
#     # DATE_2025_05_01 (index 3) for schedule_date
#     await seed_dates([test_dates_data[3]])
#     await seed_users(test_users_data[:2])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_schedule_date_types([test_schedule_date_types_data[0]])
#     await seed_schedule_dates([test_schedule_dates_data[0]])
#     await seed_media_roles([test_media_roles_data[0]])
#     await seed_schedule_date_roles([test_schedule_date_roles_data[0]])
    
#     response = await async_client.patch(f"/event_assignments/{EVENT_ASSIGNMENT_ID_1}", json=payload)
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     for field, expected_value in expected_fields.items():
#         assert response_json[field] == expected_value

# # =============================
# # DELETE EVENT ASSIGNMENT
# # =============================
# @pytest.mark.parametrize("event_assignment_id, expected_status", [
#     # Schedule date role not found
#     (BAD_ID_0000, status.HTTP_404_NOT_FOUND),
#     # Invalid UUID format
#     ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
# ])
# @pytest.mark.asyncio
# async def test_delete_event_assignment_error_cases(async_client, event_assignment_id, expected_status):
#     """Test DELETE event assignment error cases (404 and 422)"""
#     response = await async_client.delete(f"/event_assignments/{event_assignment_id}")
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_delete_event_assignment_success(async_client, seed_dates, seed_schedules, seed_schedule_date_types, seed_schedule_dates, seed_media_roles, seed_schedule_date_roles, test_dates_data, test_schedules_data, test_schedule_date_types_data, test_schedule_dates_data, test_media_roles_data, test_schedule_date_roles_data):
#     """Test successful event assignment deletion with verification"""
#     # DATE_2025_05_01 (index 3) for schedule_date
#     await seed_dates([test_dates_data[3], test_dates_data[4]])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_schedule_date_types([test_schedule_date_types_data[0]])
#     await seed_schedule_dates([test_schedule_dates_data[0]])
#     await seed_media_roles(test_media_roles_data[:2])
#     await seed_schedule_date_roles([test_schedule_date_roles_data[1]])

#     response = await async_client.delete(f"/event_assignments/{EVENT_ASSIGNMENT_ID_2}")
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     assert isinstance(response_json, dict)
#     assert response_json["event_assignment_id"] == EVENT_ASSIGNMENT_ID_2

#     # Verify deletion by trying to get it again
#     verify_response = await async_client.get(f"/event_assignments/{EVENT_ASSIGNMENT_ID_2}")
#     assert verify_response.status_code == status.HTTP_404_NOT_FOUND
