import pytest
import json
from fastapi import status
from sqlmodel import select, func

pytestmark = pytest.mark.asyncio

from app.db.models import EventAssignment
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, parse_to_utc, conditional_seed
from tests.utils.constants import (
    BAD_ID_0000, SCHEDULE_ID_1, SCHEDULE_ID_2, EVENT_TYPE_ID_1, EVENT_TYPE_ID_2,
    EVENT_ID_1, EVENT_ID_2, EVENT_ID_3, TEAM_ID_1, USER_ID_1, ROLE_ID_1, ROLE_ID_2, EVENT_ASSIGNMENT_ID_1, EVENT_ASSIGNMENT_ID_2,
    DATETIME_2025_05_01, DATETIME_2025_05_02, DATETIME_2025_05_03, DATETIME_2025_05_04
)

VALID_INSERT_PAYLOAD = {
    "title": "New Event",
    "starts_at": DATETIME_2025_05_01.isoformat(),
    "ends_at": DATETIME_2025_05_02.isoformat(),
    "event_type_id": EVENT_TYPE_ID_1
}
VALID_UPDATE_PAYLOAD = {
    "title": "Updated Event",
    "starts_at": DATETIME_2025_05_03.isoformat(),
    "ends_at": DATETIME_2025_05_04.isoformat(),
    "team_id": TEAM_ID_1,
    "event_type_id": EVENT_TYPE_ID_2,
    "notes": "Updated notes",
    "is_active": False
}

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
async def test_get_all_events_for_schedule_none_exist(async_client, seed_schedules, test_schedules_data):
    seed_schedules([test_schedules_data[0]])
    response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}/events")
    assert_empty_list_200(response)

async def test_get_all_events_for_schedule_success(async_client, seed_for_events_tests):
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

    events_dict = {obj["event"]["id"]: obj for obj in response_json}
    assert events_dict[EVENT_ID_1]["event"]["id"] is not None
    assert events_dict[EVENT_ID_1]["event"]["schedule_id"] == SCHEDULE_ID_2
    assert events_dict[EVENT_ID_2]["event"]["event_type_id"] == EVENT_TYPE_ID_1
    assert parse_to_utc(events_dict[EVENT_ID_2]["event"]["starts_at"]) == DATETIME_2025_05_02
    assert parse_to_utc(events_dict[EVENT_ID_3]["event"]["ends_at"]) == DATETIME_2025_05_04
    assert events_dict[EVENT_ID_3]["event"]["team_id"] is None
    event_assignments_dict = {ea["role_id"]: ea for ea in events_dict[EVENT_ID_1]["event_assignments"]}
    assert event_assignments_dict[ROLE_ID_1]["id"] is not None
    assert event_assignments_dict[ROLE_ID_1]["role_id"] == ROLE_ID_1
    assert event_assignments_dict[ROLE_ID_1]["role_name"] == "ProPresenter"
    assert event_assignments_dict[ROLE_ID_1]["is_applicable"] is True
    assert event_assignments_dict[ROLE_ID_1]["requirement_level"] == "REQUIRED"
    assert event_assignments_dict[ROLE_ID_1]["assigned_user_id"] == USER_ID_1
    assert event_assignments_dict[ROLE_ID_1]["assigned_user_first_name"] == "Alice"

# =============================
# GET SINGLE EVENT
# =============================
@pytest.mark.parametrize("event_id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Event not found
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
async def test_get_single_event_error_cases(async_client, event_id, expected_status):
    response = await async_client.get(f"/events/{event_id}")
    assert response.status_code == expected_status

async def test_get_single_event_success(async_client, seed_for_events_tests):
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

# =============================
# INSERT EVENT FOR SCHEDULE
# =============================
@pytest.mark.parametrize("schedule_id, payload, expected_status", [
    (BAD_ID_0000, VALID_INSERT_PAYLOAD, status.HTTP_404_NOT_FOUND), # schedule not found
    (SCHEDULE_ID_2, {}, status.HTTP_422_UNPROCESSABLE_CONTENT), # empty payload
    (SCHEDULE_ID_2, {"title": "New Event"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # missing required fields
    (SCHEDULE_ID_2, {**VALID_INSERT_PAYLOAD, "starts_at": "invalid-datetime"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid format in payload
    (SCHEDULE_ID_2, {"id": EVENT_ID_1, **VALID_INSERT_PAYLOAD}, status.HTTP_422_UNPROCESSABLE_CONTENT), # extra fields not allowed
    (SCHEDULE_ID_2, {**VALID_INSERT_PAYLOAD, "starts_at": DATETIME_2025_05_03.isoformat()}, status.HTTP_422_UNPROCESSABLE_CONTENT), # starts_at is before ends_at
    (SCHEDULE_ID_2, {**VALID_INSERT_PAYLOAD, "event_type_id": BAD_ID_0000}, status.HTTP_409_CONFLICT), # foreign key violation (event_type doesn't exist)
])
async def test_insert_event_for_schedule_error_cases(
    async_client, seed_schedules, seed_event_types, test_schedules_data, test_event_types_data, 
    schedule_id, payload, expected_status
):
    seed_event_types([test_event_types_data[0]])
    seed_schedules([test_schedules_data[1]])
    response = await async_client.post(f"/schedules/{schedule_id}/events", json=payload)
    assert response.status_code == expected_status

async def test_insert_event_for_schedule_success(async_client, seed_schedules, seed_event_types, seed_roles, test_schedules_data, test_event_types_data, test_roles_data):
    seed_roles([test_roles_data[0]])
    seed_schedules([test_schedules_data[1]])
    seed_event_types([test_event_types_data[0]])
    response = await async_client.post(f"/schedules/{SCHEDULE_ID_2}/events", json=VALID_INSERT_PAYLOAD)
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()

    # shape assertions
    assert "event" in response_json
    assert "event_assignments" in response_json

    event = response_json["event"]
    assert "id" in event
    assert "schedule_id" in event
    assert "event_type_id" in event
    assert "starts_at" in event
    assert "ends_at" in event
    assert "team_id" in event

    for ea in response_json["event_assignments"]:
        assert "id" in ea
        assert "role_id" in ea
        assert "role_name" in ea
        assert "is_applicable" in ea
        assert "requirement_level" in ea
        assert "assigned_user_id" in ea
        assert "assigned_user_first_name" in ea

    # data assertions
    assert response_json["event"]["id"] is not None
    assert response_json["event"]["schedule_id"] == SCHEDULE_ID_2
    assert response_json["event"]["event_type_id"] == EVENT_TYPE_ID_1
    assert parse_to_utc(response_json["event"]["starts_at"]) == DATETIME_2025_05_01
    assert parse_to_utc(response_json["event"]["ends_at"]) == DATETIME_2025_05_02
    event_assignments_dict = {ea["role_id"]: ea for ea in response_json["event_assignments"]}
    assert event_assignments_dict[ROLE_ID_1]["id"] is not None
    assert event_assignments_dict[ROLE_ID_1]["role_id"] == ROLE_ID_1
    assert event_assignments_dict[ROLE_ID_1]["role_name"] == "ProPresenter"
    assert event_assignments_dict[ROLE_ID_1]["is_applicable"] is True
    assert event_assignments_dict[ROLE_ID_1]["requirement_level"] == "REQUIRED"
    assert event_assignments_dict[ROLE_ID_1]["assigned_user_id"] is None
    assert event_assignments_dict[ROLE_ID_1]["assigned_user_first_name"] is None

# =============================
# UPDATE EVENT
# =============================
@pytest.mark.parametrize("event_id, payload, expected_status", [
    (BAD_ID_0000, {"notes": "Updated notes"}, status.HTTP_404_NOT_FOUND), # event not found
    ("invalid-uuid-format", {"notes": "Updated notes"}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (EVENT_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (EVENT_ID_1, {"event_type_id": BAD_ID_0000}, status.HTTP_409_CONFLICT), # FK violation
    (EVENT_ID_1, {"title": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (EVENT_ID_1, {"title": "Invalid", "id": BAD_ID_0000}, status.HTTP_422_UNPROCESSABLE_CONTENT), # extra fields not allowed
])
async def test_update_event_error_cases(async_client, seed_event_types, seed_schedules, seed_events, test_events_data, test_event_types_data, test_schedules_data, event_id, payload, expected_status):
    seed_event_types([test_event_types_data[0]])
    seed_schedules([test_schedules_data[1]])
    seed_events([test_events_data[0]])
    response = await async_client.patch(f"/events/{event_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    (VALID_UPDATE_PAYLOAD, {}), # full update
    ({"is_active": False}, {"title": None, "starts_at": DATETIME_2025_05_01.isoformat(), "ends_at": DATETIME_2025_05_02.isoformat(), "event_type_id": EVENT_TYPE_ID_1, "notes": None, "team_id": None}), # partial update (is_active only)
    ({"title": "Partially Updated Event"}, {"starts_at": DATETIME_2025_05_01.isoformat(), "ends_at": DATETIME_2025_05_02.isoformat(), "event_type_id": EVENT_TYPE_ID_1, "notes": None, "is_active": True, "team_id": None}), # partial update (title only)
])
async def test_update_event_success(async_client, seed_schedules, seed_event_types, seed_teams, seed_events, test_schedules_data, test_event_types_data, test_teams_data, test_events_data, payload, unchanged_fields):
    seed_schedules([test_schedules_data[1]])
    seed_event_types(test_event_types_data[:2])
    seed_teams([test_teams_data[0]])
    seed_events([test_events_data[0]])
    response = await async_client.patch(f"/events/{EVENT_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        if field in ("starts_at", "ends_at"):
            assert parse_to_utc(response_json[field]).isoformat() == value
        else:
            assert response_json[field] == value
    for field, value in unchanged_fields.items():
        if field in ("starts_at", "ends_at"):
            assert parse_to_utc(response_json[field]).isoformat() == value
        else:
            assert response_json[field] == value

# =============================
# DELETE EVENT
# =============================
async def test_delete_event_error_cases(async_client):
    response = await async_client.delete("/events/invalid-uuid-format")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_delete_event_success(async_client, seed_events, seed_event_types, seed_schedules, test_events_data, test_event_types_data, test_schedules_data):
    seed_event_types([test_event_types_data[0]])
    seed_schedules([test_schedules_data[1]])
    seed_events([test_events_data[0]])
    response = await async_client.delete(f"/events/{EVENT_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/events/{EVENT_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

# =============================
# DELETE EVENT CASCADE
# =============================
@pytest.mark.parametrize("event_assignment_indices, expected_count_before", [
    ([], 0), # No event_assignments to cascade delete
    ([0], 1), # One event_assignment to cascade delete
    ([0, 1], 2), # Multiple event_assignments to cascade delete
])
async def test_delete_event_cascade_event_assignments(
    async_client, get_test_db_session, seed_users, seed_schedules, seed_event_types, seed_events, seed_roles, seed_event_assignments,
    test_users_data, test_schedules_data, test_event_types_data, test_events_data, test_roles_data, test_event_assignments_data,
    event_assignment_indices, expected_count_before
):
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