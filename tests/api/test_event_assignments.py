import pytest
from fastapi import status

from tests.utils.helpers import assert_empty_list_200, assert_list_200
from tests.utils.constants import BAD_ID_0000, EVENT_ID_1, ROLE_ID_1, USER_ID_1, USER_ID_2, EVENT_ASSIGNMENT_ID_1, EVENT_ASSIGNMENT_ID_2, SCHEDULE_ID_2

VALID_UPDATE_PAYLOAD = {
    "requirement_level": "OPTIONAL",
    "assigned_user_id": USER_ID_2,
    "is_active": False
}

# =============================
# FIXTURES
# =============================
@pytest.fixture
def seed_for_event_assignments_tests(seed_roles, seed_proficiency_levels, seed_users, seed_user_roles, seed_schedules, seed_event_types, seed_events, seed_event_assignments, test_roles_data, test_proficiency_levels_data, test_users_data, test_user_roles_data, test_schedules_data, test_event_types_data, test_events_data, test_event_assignments_data):
    seed_roles(test_roles_data[:2])
    seed_proficiency_levels(test_proficiency_levels_data[:2])
    seed_users(test_users_data[:2])
    seed_user_roles(test_user_roles_data[:2])
    seed_schedules([test_schedules_data[1]])
    seed_event_types([test_event_types_data[0]])
    seed_events([test_events_data[0]])
    seed_event_assignments(test_event_assignments_data[:2])

# =============================
# GET ALL EVENT ASSIGNMENTS FOR EVENT
# =============================
@pytest.mark.asyncio
async def test_get_all_event_assignments_for_event_none_exist(async_client, seed_schedules, seed_event_types, seed_events, test_schedules_data, test_event_types_data, test_events_data):
    seed_schedules([test_schedules_data[1]])
    seed_event_types([test_event_types_data[0]])
    seed_events([test_events_data[0]])
    response = await async_client.get(f"/events/{EVENT_ID_1}/assignments")
    assert_empty_list_200(response)

@pytest.mark.asyncio
async def test_get_all_event_assignments_for_event_success(async_client, seed_for_event_assignments_tests):
    response = await async_client.get(f"/events/{EVENT_ID_1}/assignments")
    assert_list_200(response, expected_length=2)
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
    assert response_json[1]["event_type_code"] == "service"
    assert response_json[1]["role_code"] == "sound"

# =============================
# UPDATE EVENT ASSIGNMENT
# =============================
@pytest.mark.parametrize("assignment_id, payload, expected_status", [
    (BAD_ID_0000, VALID_UPDATE_PAYLOAD, status.HTTP_404_NOT_FOUND), # assignment not found
    ("invalid-uuid-format", VALID_UPDATE_PAYLOAD, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid UUID format
    (EVENT_ASSIGNMENT_ID_1, {}, status.HTTP_400_BAD_REQUEST), # empty payload
    (EVENT_ASSIGNMENT_ID_1, {"requirement_level": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT), # invalid data types
    (EVENT_ASSIGNMENT_ID_1, {"assigned_user_id": BAD_ID_0000}, status.HTTP_409_CONFLICT), # FK violation
    (EVENT_ASSIGNMENT_ID_1, {"requirement_level": "OPTIONAL", "id": EVENT_ASSIGNMENT_ID_2}, status.HTTP_422_UNPROCESSABLE_CONTENT), # non-updatable field
])
@pytest.mark.asyncio
async def test_update_event_assignment_error_cases(async_client, seed_for_event_assignments_tests, assignment_id, payload, expected_status):
    response = await async_client.patch(f"/assignments/{assignment_id}", json=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize("payload, unchanged_fields", [
    (VALID_UPDATE_PAYLOAD, {}), # full update
    ({"is_active": False}, {"requirement_level": "REQUIRED", "assigned_user_id": USER_ID_1}), # partial update (is_active only)
    ({"requirement_level": "OPTIONAL"}, {"assigned_user_id": USER_ID_1, "is_active": True}), # partial update (requirement_level only)
])
@pytest.mark.asyncio
async def test_update_event_assignment_success(async_client, seed_for_event_assignments_tests, payload, unchanged_fields):
    response = await async_client.patch(f"/assignments/{EVENT_ASSIGNMENT_ID_1}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, value in payload.items():
        assert response_json[field] == value
    for field, value in unchanged_fields.items():
        assert response_json[field] == value