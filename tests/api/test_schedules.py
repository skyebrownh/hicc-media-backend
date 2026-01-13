import pytest
from fastapi import status
from sqlmodel import select, func

from app.db.models import Event, EventAssignment
from tests.utils.helpers import assert_empty_list_200, assert_list_200, assert_single_item_200, assert_single_item_201, conditional_seed
from tests.utils.constants import BAD_ID_0000, SCHEDULE_ID_1, SCHEDULE_ID_2, ROLE_ID_1, ROLE_ID_2, USER_ID_1, EVENT_ID_1, EVENT_ID_2, EVENT_ID_3, EVENT_TYPE_ID_1

# =============================
# FIXTURES
# =============================
@pytest.fixture
def seed_for_schedules_tests(seed_roles, seed_users, seed_schedules, seed_event_types, seed_events, seed_event_assignments, seed_user_unavailable_periods, test_roles_data, test_users_data, test_schedules_data, test_event_types_data, test_events_data, test_event_assignments_data, test_user_unavailable_periods_data):
    seed_roles(test_roles_data[:2])
    seed_users(test_users_data[:2])
    seed_schedules([test_schedules_data[1]])
    seed_event_types([test_event_types_data[0]])
    seed_events(test_events_data)
    seed_event_assignments(test_event_assignments_data)
    seed_user_unavailable_periods(test_user_unavailable_periods_data[-2:])

# =============================
# GET ALL SCHEDULES
# =============================
@pytest.mark.asyncio
async def test_get_all_schedules_none_exist(async_client):
    response = await async_client.get("/schedules")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_schedules_success(async_client, seed_schedules, test_schedules_data):
    seed_schedules(test_schedules_data)
    response = await async_client.get("/schedules")
    assert_list_200(response, expected_length=2)
    response_json = response.json()
    assert response_json[0]["month"] == 1
    assert response_json[0]["year"] == 2025
    assert response_json[1]["id"] is not None
    assert response_json[1]["month"] == 5
    assert response_json[1]["year"] == 2025
    assert response_json[1]["notes"] == "Second schedule"
    assert response_json[1]["is_active"] is True

# =============================
# GET SINGLE SCHEDULE
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Schedule not present
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_single_schedule_error_cases(async_client, id, expected_status):
    response = await async_client.get(f"/schedules/{id}")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_single_schedule_success(async_client, seed_schedules, test_schedules_data):
    seed_schedules([test_schedules_data[0]])
    response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}")
    assert_single_item_200(response, expected_item={
        "id": SCHEDULE_ID_1,
        "month": 1,
        "year": 2025,
        "notes": "First schedule",
        "is_active": True
    })

# =============================
# GET SCHEDULE GRID
# =============================
@pytest.mark.parametrize("id, expected_status", [
    (BAD_ID_0000, status.HTTP_404_NOT_FOUND), # Schedule not found
    ("invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT), # Invalid UUID format
])
@pytest.mark.asyncio
async def test_get_schedule_grid_error_cases(async_client, id, expected_status):
    response = await async_client.get(f"/schedules/{id}/grid")
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_schedule_grid_success(async_client, seed_for_schedules_tests):
    response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}/grid")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["schedule"]["id"] == SCHEDULE_ID_2
    assert response_json["schedule"]["month"] == 5
    assert response_json["schedule"]["notes"] == "Second schedule"
    assert len(response_json["events"]) == 3
    assert response_json["events"][0]["event"]["id"] == EVENT_ID_1
    assert response_json["events"][0]["event"]["event_type_id"] == EVENT_TYPE_ID_1
    assert response_json["events"][0]["event"]["team_id"] is None
    assert response_json["events"][1]["event"]["id"] == EVENT_ID_2
    assert len(response_json["events"][0]["event_assignments"]) == 2
    assert response_json["events"][0]["event_assignments"][0]["role_id"] == ROLE_ID_1
    assert response_json["events"][0]["event_assignments"][0]["assigned_user_id"] == USER_ID_1
    assert response_json["events"][0]["event_assignments"][1]["role_id"] == ROLE_ID_2
    assert response_json["events"][0]["event_assignments"][1]["assigned_user_id"] is None
    assert len(response_json["events"][0]["availability"]) == 2
    assert response_json["events"][0]["availability"][0]["user_first_name"] == "Alice"
    assert response_json["events"][0]["availability"][0]["user_last_name"] == "Smith"
    assert response_json["events"][0]["availability"][1]["user_first_name"] == "Bob"
    assert response_json["events"][0]["availability"][1]["user_last_name"] == "Jones"

# =============================
# INSERT SCHEDULE
# =============================
@pytest.mark.parametrize("payload", [
    ({}), # empty payload
    ({ "month": 13, "year": 2025}), # invalid month - violates check constraint
    ({ "month": 5, "year": "two thousand twenty four"}), # invalid year
    ({ "id": BAD_ID_0000, "month": 5, "year": 2025}), # schedule_id not allowed in payload
])
@pytest.mark.asyncio
async def test_insert_schedule_error_cases(async_client, payload):
    response = await async_client.post("/schedules", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_insert_schedule_success(async_client):
    response = await async_client.post("/schedules", json={"month": 10, "year": 2025})
    assert_single_item_201(response, expected_item={"month": 10, "year": 2025, "notes": None, "is_active": True})

# =============================
# UPDATE SCHEDULE
# =============================
@pytest.mark.parametrize("schedule_id, payload, expected_status", [
    (BAD_ID_0000, {"notes": "Updated Notes", "is_active": False}, status.HTTP_404_NOT_FOUND), # schedule not found
    ("invalid-uuid-format", {"notes": "Updated Notes", "is_active": False}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (SCHEDULE_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (SCHEDULE_ID_1, {"notes": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (SCHEDULE_ID_1, {"notes": "Invalid", "id": SCHEDULE_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
@pytest.mark.asyncio
async def test_update_schedule_error_cases(async_client, seed_schedules, test_schedules_data, schedule_id, payload, expected_status):
    seed_schedules([test_schedules_data[0]])
    response = await async_client.patch(f"/schedules/{schedule_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    ({"notes": "Updated Notes", "is_active": False}, {}), # full update
    ({"is_active": False}, {"notes": "First schedule"}), # partial update (is_active only)
    ({"notes": "Partially Updated Schedule"}, {"is_active": True}), # partial update (schedule_notes only)
])
@pytest.mark.asyncio
async def test_update_schedule_success(async_client, seed_schedules, test_schedules_data, payload, unchanged_fields):
    seed_schedules([test_schedules_data[0]])
    response = await async_client.patch(f"/schedules/{SCHEDULE_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == getattr(test_schedules_data[0], field)

# =============================
# DELETE SCHEDULE
# =============================
@pytest.mark.asyncio
async def test_delete_schedule_error_cases(async_client):
    response = await async_client.delete("/schedules/invalid-uuid-format")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_delete_schedule_success(async_client, seed_schedules, test_schedules_data):
    seed_schedules([test_schedules_data[0]])
    response = await async_client.delete(f"/schedules/{SCHEDULE_ID_1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/schedules/{SCHEDULE_ID_1}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

# =============================
# DELETE SCHEDULE CASCADE
# =============================
@pytest.mark.parametrize("event_indices, event_assignment_indices, expected_count_events_before, expected_count_event_assignments_before", [
    ([], [], 0, 0), # No events to cascade delete
    ([0], [], 1, 0), # One event, no event_assignments to cascade delete
    ([0, 1], [], 2, 0), # Multiple events, no event_assignments to cascade delete
    ([0], [0], 1, 1), # One event, one event_assignment to cascade delete
    ([0], [0, 1], 1, 2), # One event, multiple event_assignments to cascade delete
    ([0, 1], [], 2, 0), # Multiple events, no event_assignments to cascade delete
    ([0, 1], [0, 2], 2, 2), # Multiple events, one event_assignment to cascade delete
    ([0, 1, 2], [0, 1, 2], 3, 3), # Multiple events, multiple event_assignments to cascade delete
])
@pytest.mark.asyncio
async def test_delete_schedule_cascade(
    async_client, get_test_db_session, seed_schedules, seed_roles, seed_users, seed_event_types, seed_events, seed_event_assignments,
    test_schedules_data, test_roles_data, test_users_data, test_event_types_data, test_events_data, test_event_assignments_data,
    event_indices, event_assignment_indices, expected_count_events_before, expected_count_event_assignments_before
):
    # Seed parent
    seed_schedules([test_schedules_data[1]])

    # Seed child records based on parameters
    seed_roles(test_roles_data[:2])
    seed_users([test_users_data[0]])
    seed_event_types([test_event_types_data[0]])
    conditional_seed(event_indices, test_events_data, seed_events)
    conditional_seed(event_assignment_indices, test_event_assignments_data, seed_event_assignments)

    # Select event_assignment_ids that will be deleted
    event_assignment_ids = [test_event_assignments_data[i].id for i in event_assignment_indices]

    # Verify child records exist before deletion
    count_events_before = get_test_db_session.exec(select(func.count()).select_from(Event).where(Event.schedule_id == SCHEDULE_ID_2)).one()
    assert count_events_before == expected_count_events_before
    count_event_assignments_before = get_test_db_session.exec(select(func.count()).select_from(EventAssignment).where(EventAssignment.id.in_(event_assignment_ids))).one()
    assert count_event_assignments_before == expected_count_event_assignments_before

    # Delete parent
    response = await async_client.delete(f"/schedules/{SCHEDULE_ID_2}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify parent is deleted
    verify_response = await async_client.get(f"/schedules/{SCHEDULE_ID_2}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    # Verify all child records are cascade deleted
    count_events_after = get_test_db_session.exec(select(func.count()).select_from(Event).where(Event.schedule_id == SCHEDULE_ID_2)).one()
    assert count_events_after == 0
    count_event_assignments_after = get_test_db_session.exec(select(func.count()).select_from(EventAssignment).where(EventAssignment.id.in_(event_assignment_ids))).one()
    assert count_event_assignments_after == 0
