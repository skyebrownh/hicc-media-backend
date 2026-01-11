import pytest
from fastapi import HTTPException, status
from app.utils.helpers import (
    raise_exception_if_not_found,
    build_events_with_assignments_from_schedule,
    build_events_with_assignments_from_event,
)
from app.db.models import ProficiencyLevel, Role
from tests.utils.constants import (
    BAD_ID_0000, 
    PROFICIENCY_LEVEL_ID_1,
    ROLE_ID_1,
    SCHEDULE_ID_2,
    EVENT_ID_1,
    USER_ID_1,
    EVENT_TYPE_ID_1,
    EVENT_ASSIGNMENT_ID_1,
)

# =============================
# TEST DATA FIXTURES
# =============================
@pytest.fixture
def sample_schedule_with_events(
    test_users_data,
    test_roles_data,
    test_schedules_data,
    test_event_types_data,
    test_events_data,
    test_event_assignments_data,
):
    """Create a sample Schedule with Events and related objects in memory using shared test data."""
    # Get objects from shared fixtures
    event_type = test_event_types_data[0]
    schedule = test_schedules_data[1]
    user_1 = test_users_data[0]
    role_1 = test_roles_data[0]
    role_2 = test_roles_data[1]
    
    # Get events and assignments
    event_1 = test_events_data[0]
    event_2 = test_events_data[1]
    event_3 = test_events_data[2]
    event_assignment_1 = test_event_assignments_data[0]
    event_assignment_2 = test_event_assignments_data[1]
    
    # Set up relationships
    event_1.schedule = schedule
    event_1.event_type = event_type
    event_1.team = None
    
    event_2.schedule = schedule
    event_2.event_type = event_type
    event_2.team = None
    
    event_3.schedule = schedule
    event_3.event_type = event_type
    event_3.team = None
    
    event_assignment_1.event = event_1
    event_assignment_1.role = role_1
    event_assignment_1.assigned_user = user_1
    
    event_assignment_2.event = event_1
    event_assignment_2.role = role_2
    event_assignment_2.assigned_user = None
    
    # Set up event assignments lists
    event_1.event_assignments = [event_assignment_1, event_assignment_2]
    event_2.event_assignments = []
    event_3.event_assignments = []
    
    schedule.events = [event_1, event_2, event_3]
    
    return schedule

@pytest.fixture
def sample_event_with_assignments(sample_schedule_with_events):
    """Create a sample Event with assignments in memory."""
    return sample_schedule_with_events.events[0]

@pytest.fixture
def sample_schedule_with_availability(
    sample_schedule_with_events,
    test_users_data,
    test_user_unavailable_periods_data,
):
    """Create a sample Schedule with events that have availability information."""
    schedule = sample_schedule_with_events
    
    # Get users and unavailable periods from shared fixtures
    user_1 = test_users_data[0]
    user_2 = test_users_data[1]
    unavailable_period_1 = test_user_unavailable_periods_data[6]  # May 1-2 for user 1
    unavailable_period_2 = test_user_unavailable_periods_data[7]  # May 1-2 for user 2
    
    # Set up user relationships
    unavailable_period_1.user = user_1
    unavailable_period_2.user = user_2
    
    # Set availability on first event
    # Note: This assumes event.availability exists as a relationship or attribute
    schedule.events[0].availability = [unavailable_period_1, unavailable_period_2]
    schedule.events[1].availability = []
    schedule.events[2].availability = []
    
    return schedule

# =============================
# TESTS
# =============================
def test_raise_exception_if_not_found():
    """Test raise_exception_if_not_found function"""
    # Test: raises 404 when object is None with default status code
    with pytest.raises(HTTPException) as exc_info:
        raise_exception_if_not_found(None, ProficiencyLevel)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "ProficiencyLevel not found"

    # Test: raises custom status code when object is None
    with pytest.raises(HTTPException) as exc_info:
        raise_exception_if_not_found(None, Role, http_status_code=status.HTTP_400_BAD_REQUEST)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Role not found"

    # Test: does nothing when object exists
    proficiency_level = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_1, name="Beginner", code="beginner")
    raise_exception_if_not_found(proficiency_level, ProficiencyLevel)
    assert str(proficiency_level.id) == str(PROFICIENCY_LEVEL_ID_1)

def test_build_events_with_assignments_from_schedule(sample_schedule_with_events):
    """Test build_events_with_assignments_from_schedule function"""
    # Build events with assignments from in-memory schedule
    result = build_events_with_assignments_from_schedule(sample_schedule_with_events)
    
    # Assertions
    assert isinstance(result, list)
    assert len(result) == 3  # Three events in test data
    
    # Check first event structure
    first_event = result[0]
    assert str(first_event.event.id) == EVENT_ID_1
    assert str(first_event.event.schedule_id) == SCHEDULE_ID_2
    assert str(first_event.event.event_type_id) == EVENT_TYPE_ID_1
    assert len(first_event.event_assignments) == 2  # Two assignments for first event
    
    # Check event assignment structure
    first_assignment = first_event.event_assignments[0]
    assert str(first_assignment.id) == EVENT_ASSIGNMENT_ID_1
    assert str(first_assignment.role_id) == ROLE_ID_1
    assert first_assignment.role_name == "ProPresenter"
    assert str(first_assignment.assigned_user_id) == USER_ID_1
    assert first_assignment.assigned_user_first_name == "Alice"

def test_build_events_with_assignments_from_event(sample_event_with_assignments):
    """Test build_events_with_assignments_from_event function"""
    # Build event with assignments from in-memory event
    result = build_events_with_assignments_from_event(sample_event_with_assignments)
    
    # Assertions
    assert str(result.event.id) == EVENT_ID_1
    assert str(result.event.schedule_id) == SCHEDULE_ID_2
    assert str(result.event.event_type_id) == EVENT_TYPE_ID_1
    assert len(result.event_assignments) == 2  # Two assignments for first event
    
    # Check event assignment structure
    first_assignment = result.event_assignments[0]
    assert str(first_assignment.id) == EVENT_ASSIGNMENT_ID_1
    assert str(first_assignment.role_id) == ROLE_ID_1
    assert first_assignment.role_name == "ProPresenter"
    assert str(first_assignment.assigned_user_id) == USER_ID_1
    assert first_assignment.assigned_user_first_name == "Alice"