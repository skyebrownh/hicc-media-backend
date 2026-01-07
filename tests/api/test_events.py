import pytest
import json
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, parse_to_utc, conditional_seed
from sqlmodel import select, func
from app.db.models import EventAssignment
from tests.utils.constants import (
    BAD_ID_0000, SCHEDULE_ID_1, SCHEDULE_ID_2, EVENT_TYPE_ID_1, EVENT_TYPE_ID_2,
    EVENT_ID_1, EVENT_ID_2, EVENT_ID_3, TEAM_ID_1, USER_ID_1, USER_ID_2, ROLE_ID_1, ROLE_ID_2, EVENT_ASSIGNMENT_ID_1, EVENT_ASSIGNMENT_ID_2,
    DATETIME_2025_05_01, DATETIME_2025_05_02, DATETIME_2025_05_03, DATETIME_2025_05_04
)

# =============================
# FIXTURES
# =============================
@pytest.fixture
def seed_for_events_tests(seed_users, seed_roles, seed_schedules, seed_event_types, seed_events, seed_event_assignments, test_users_data, test_roles_data, test_schedules_data, test_event_types_data, test_events_data, test_event_assignments_data):
    seed_users([test_users_data[0]])
    seed_roles(test_roles_data[:2])
    seed_schedules([test_schedules_data[1]])
    seed_event_types([test_event_types_data[0]])
    seed_events(test_events_data)
    seed_event_assignments(test_event_assignments_data[:2])

# =============================
# GET ALL EVENTS FOR SCHEDULE
# =============================
@pytest.mark.asyncio
async def test_get_all_events_for_schedule_none_exist(async_client, seed_schedules, test_schedules_data):
    """Test GET all events for schedule when none exist returns empty list"""
    seed_schedules([test_schedules_data[0]])
    response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/events")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_events_for_schedule_success(async_client, seed_for_events_tests):
    """Test GET all events for schedule success case"""
    response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}/events")
    assert_list_200(response, expected_length=3)
    response_json = response.json()
    print(f"GET all events for schedule response_json: {json.dumps(response_json, indent=4)}")

    # shape assertions
    for obj in response_json:
        assert "event" in obj
        assert "event_assignments" in obj
        
        event = obj["event"]
        assert "id" in event
        assert "schedule_id" in event
        assert "event_type_id" in event
        assert "starts_at" in event
        assert "ends_at" in event
        assert "team_id" in event

        for ea in obj["event_assignments"]:
            assert "id" in ea
            assert "role_id" in ea
            assert "role_name" in ea
            assert "is_applicable" in ea
            assert "requirement_level" in ea
            assert "assigned_user_id" in ea
            assert "assigned_user_first_name" in ea

    assert response_json[0]["event"]["id"] is not None
    assert response_json[0]["event"]["schedule_id"] == SCHEDULE_ID_2
    assert response_json[1]["event"]["event_type_id"] == EVENT_TYPE_ID_1
    assert parse_to_utc(response_json[1]["event"]["starts_at"]) == DATETIME_2025_05_02
    assert parse_to_utc(response_json[2]["event"]["ends_at"]) == DATETIME_2025_05_04
    assert response_json[2]["event"]["team_id"] is None
    assert response_json[0]["event_assignments"][0]["id"] is not None
    assert response_json[0]["event_assignments"][0]["role_id"] == ROLE_ID_1
    assert response_json[0]["event_assignments"][0]["role_name"] == "ProPresenter"
    assert response_json[0]["event_assignments"][0]["is_applicable"] is True
    assert response_json[0]["event_assignments"][0]["requirement_level"] == "REQUIRED"
    assert response_json[0]["event_assignments"][0]["assigned_user_id"] == USER_ID_1
    assert response_json[0]["event_assignments"][0]["assigned_user_first_name"] == "Alice"

# =============================
# GET SINGLE EVENT
# =============================
@pytest.mark.parametrize("event_id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Event not found
    ("invalid-uuid-format", status.HTTP_400_BAD_REQUEST), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_event_error_cases(async_client, event_id, expected_status):
    """Test GET single schedule date error cases (400, 404)"""
    response = await async_client.get(f"/events/{event_id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_event_success(async_client, seed_for_events_tests):
    """Test GET single event success case"""
    response = await async_client.get(f"/events/{EVENT_ID_1}")
    response_json = response.json()
    assert parse_to_utc(response_json["event"]["starts_at"]) == DATETIME_2025_05_01
    assert parse_to_utc(response_json["event"]["ends_at"]) == DATETIME_2025_05_02
    
    assert_single_item_200(response, expected_item={
        "event": {
            "id": EVENT_ID_1,
            "title": None,
            "schedule_id": SCHEDULE_ID_2,
            "team_id": None,
            "event_type_id": EVENT_TYPE_ID_1,
            "notes": None,
            "is_active": True,
            "schedule_month": 5,
            "schedule_year": 2025,
            "schedule_notes": "Second schedule",
            "schedule_is_active": True,
            "team_name": None,
            "team_code": None,
            "team_is_active": None,
            "event_type_name": "Service",
            "event_type_code": "service",
            "event_type_is_active": True
        },
        "event_assignments": [
            {
                "id": EVENT_ASSIGNMENT_ID_1,
                "role_id": ROLE_ID_1,
                "role_name": "ProPresenter",
                "role_order": 10,
                "role_code": "propresenter",
                "is_applicable": True,
                "requirement_level": "REQUIRED",
                "assigned_user_id": USER_ID_1,
                "assigned_user_first_name": "Alice",
                "assigned_user_last_name": "Smith",
                "is_active": True,
            },
            {
                "id": EVENT_ASSIGNMENT_ID_2,
                "role_id": ROLE_ID_2,
                "role_name": "Sound",
                "role_order": 20,
                "role_code": "sound",
                "is_applicable": True,
                "requirement_level": "REQUIRED",
                "assigned_user_id": None,
                "assigned_user_first_name": None,
                "assigned_user_last_name": None,
                "is_active": True,
            }
        ]
    })

# # =============================
# # INSERT SCHEDULE DATE
# # =============================
# @pytest.mark.parametrize("date_indices, schedule_indices, type_indices, event_indices, payload, expected_status", [
#     # empty payload
#     ([], [], [], [], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields (date and event_type_id)
#     ([], [], [], [], {"schedule_id": SCHEDULE_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # missing required fields (schedule_id and event_type_id)
#     ([], [], [], [], {"date": DATE_2025_05_02}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # invalid UUID format
#     ([], [], [], [], {"schedule_id": "invalid-uuid", "date": DATE_2025_05_02, "event_type_id": EVENT_TYPE_ID_1}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # duplicate event
#     ([3], [1], [0], [0], {"schedule_id": SCHEDULE_ID_2, "date": DATE_2025_05_01, "event_type_id": EVENT_TYPE_ID_1}, status.HTTP_409_CONFLICT),
#     # extra fields not allowed
#     ([], [], [], [], {"schedule_id": SCHEDULE_ID_2, "date": DATE_2025_05_02, "event_type_id": EVENT_TYPE_ID_1, "event_id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # foreign key violation (schedule doesn't exist)
#     ([4], [], [0], [], {"schedule_id": BAD_ID_0000, "date": DATE_2025_05_02, "event_type_id": EVENT_TYPE_ID_1}, status.HTTP_404_NOT_FOUND),
#     # foreign key violation (date doesn't exist)
#     ([3], [1], [0], [], {"schedule_id": SCHEDULE_ID_2, "date": BAD_DATE_2000_01_01, "event_type_id": EVENT_TYPE_ID_1}, status.HTTP_404_NOT_FOUND),
#     # foreign key violation (schedule_date_type doesn't exist)
#     ([3], [1], [], [], {"schedule_id": SCHEDULE_ID_2, "date": DATE_2025_05_02, "event_type_id": BAD_ID_0000}, status.HTTP_404_NOT_FOUND),
# ])
# @pytest.mark.asyncio
# async def test_insert_schedule_date_error_cases(
#     async_client, seed_dates, seed_schedules, seed_event_types, seed_events,
#     test_dates_data, test_schedules_data, test_event_types_data, test_events_data,
#     date_indices, schedule_indices, type_indices, event_indices, payload, expected_status
# ):
#     """Test INSERT event error cases (422, 409, and 404)"""
#     # Collect all dates needed
#     all_dates_needed = set()
#     # Dates from date_indices
#     if date_indices:
#         all_dates_needed.update([test_dates_data[i] for i in date_indices])
#     # Dates needed for schedules' month_start_date
#     if schedule_indices:
#         all_dates_needed.update([test_schedules_data[i]["month_start_date"] for i in schedule_indices])
#     # Dates needed for events
#     if event_indices:
#         all_dates_needed.update([test_events_data[i]["date"] for i in event_indices])
#     # Seed all dates at once
#     if all_dates_needed:
#         await seed_dates(list(all_dates_needed))
    
#     await conditional_seed(schedule_indices, test_schedules_data, seed_schedules)
#     await conditional_seed(type_indices, test_event_types_data, seed_event_types)
#     await conditional_seed(event_indices, test_events_data, seed_events)
#     response = await async_client.post("/events", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.asyncio
# async def test_insert_event_success(async_client, seed_dates, seed_schedules, seed_event_types, test_dates_data, test_schedules_data, test_event_types_data):
#     """Test valid event insertion"""
#     # DATE_2025_05_01 (index 3) for event
#     await seed_dates([test_dates_data[3]])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_event_types([test_event_types_data[0]])
    
#     response = await async_client.post("/events", json={
#         "schedule_id": SCHEDULE_ID_2,
#         "date": DATE_2025_05_01,
#         "event_type_id": EVENT_TYPE_ID_1
#     })
#     assert response.status_code == status.HTTP_201_CREATED
#     response_json = response.json()
#     assert response_json["event_id"] is not None
#     assert response_json["schedule_id"] == SCHEDULE_ID_2
#     assert response_json["date"] == DATE_2025_05_01
#     assert response_json["event_type_id"] == EVENT_TYPE_ID_1
#     assert response_json["is_active"] is True

# # =============================
# # UPDATE EVENT
# # =============================
# @pytest.mark.parametrize("event_id, payload, expected_status", [
#     # schedule date not found
#     (BAD_ID_0000, {"notes": "Updated notes"}, status.HTTP_404_NOT_FOUND),
#     # invalid UUID format
#     ("invalid-uuid-format", {"notes": "Updated notes"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
#     # empty payload
#     (EVENT_ID_1, {}, status.HTTP_400_BAD_REQUEST),
# ])
# @pytest.mark.asyncio
# async def test_update_event_error_cases(async_client, event_id, payload, expected_status):
#     """Test UPDATE event error cases (400, 404, and 422)"""
#     response = await async_client.patch(f"/events/{event_id}", json=payload)
#     assert response.status_code == expected_status

# @pytest.mark.parametrize("payload, expected_fields", [
#     # update notes
#     ({"notes": "Updated notes"}, {"notes": "Updated notes"}),
#     # update team_id
#     ({"team_id": TEAM_ID_1}, {"team_id": TEAM_ID_1}),
#     # update is_active
#     ({"is_active": False}, {"is_active": False}),
#     # update date and event_type_id
#     (
#         {"date": DATE_2025_05_02, "event_type_id": EVENT_TYPE_ID_2},
#         {"date": DATE_2025_05_02, "event_type_id": EVENT_TYPE_ID_2}
#     ),
# ])
# @pytest.mark.asyncio
# async def test_update_event_success(async_client, seed_dates, seed_schedules, seed_event_types, seed_teams, seed_events, test_dates_data, test_schedules_data, test_event_types_data, test_teams_data, test_events_data, payload, expected_fields):
#     """Test valid event updates"""
#     # DATE_2025_05_01/02/03 (indices 3,4,5) for events
#     await seed_dates([test_dates_data[3], test_dates_data[4], test_dates_data[5]])
#     await seed_schedules([test_schedules_data[1]])
#     await seed_event_types(test_event_types_data[:2])
#     await seed_teams([test_teams_data[0]])
#     await seed_events([test_events_data[0]])
    
#     response = await async_client.patch(f"/events/{EVENT_ID_1}", json=payload)
#     assert response.status_code == status.HTTP_200_OK
#     response_json = response.json()
#     for field, expected_value in expected_fields.items():
#         assert response_json[field] == expected_value

# =============================
# DELETE EVENT
# =============================
@pytest.mark.asyncio
async def test_delete_event_error_cases(async_client):
    """Test DELETE event error cases (400)"""
    response = await async_client.delete("/events/invalid-uuid-format")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_delete_event_success(async_client, seed_events, seed_event_types, seed_schedules, test_events_data, test_event_types_data, test_schedules_data):
    """Test successful event deletion with verification"""
    seed_event_types([test_event_types_data[0]])
    seed_schedules([test_schedules_data[1]])
    seed_events([test_events_data[0]])
    response = await async_client.delete(f"/events/{EVENT_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/events/{EVENT_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify valid event id that does not exist returns 204
    verify_response2 = await async_client.delete(f"/events/{BAD_ID_0000}")
    assert verify_response2.status_code == status.HTTP_204_NO_CONTENT

# =============================
# DELETE EVENT CASCADE
# =============================
@pytest.mark.parametrize("event_assignment_indices, expected_count_before", [
    ([], 0), # No event_assignments to cascade delete
    ([0], 1), # One event_assignment to cascade delete
    ([0, 1], 2), # Multiple event_assignments to cascade delete
])
@pytest.mark.asyncio
async def test_delete_event_cascade_event_assignments(
    async_client, get_test_db_session, seed_users, seed_schedules, seed_event_types, seed_events, seed_roles, seed_event_assignments,
    test_users_data, test_schedules_data, test_event_types_data, test_events_data, test_roles_data, test_event_assignments_data,
    event_assignment_indices, expected_count_before
):
    """Test that deleting a event cascades to delete associated event_assignments"""
    # Seed parent
    seed_schedules([test_schedules_data[1]])
    seed_event_types([test_event_types_data[0]])
    seed_events(test_events_data[:2])

    # Seed child records based on parameters
    seed_roles(test_roles_data[:2])
    seed_users([test_users_data[0]])
    conditional_seed(event_assignment_indices, test_event_assignments_data, seed_event_assignments)

    # Select event_assignment_ids that will be deleted
    event_assignment_ids = [test_event_assignments_data[i].id for i in event_assignment_indices]

    # Verify event_assignments exist before deletion
    count_before = get_test_db_session.exec(select(func.count()).select_from(EventAssignment).where(EventAssignment.id.in_(event_assignment_ids))).one()
    assert count_before == expected_count_before

    # Delete parent
    response = await async_client.delete(f"/events/{EVENT_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify parent is deleted
    verify_response = await async_client.get(f"/events/{EVENT_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify all child records are cascade deleted
    count_after = get_test_db_session.exec(select(func.count()).select_from(EventAssignment).where(EventAssignment.id.in_(event_assignment_ids))).one()
    assert count_after == 0