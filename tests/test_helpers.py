import pytest
from fastapi import HTTPException, status
from app.utils.helpers import (
    raise_bad_request_empty_payload, 
    get_or_404,
    build_events_with_assignments_from_schedule,
    # build_events_with_assignments_and_availability_from_schedule,
    build_events_with_assignments_from_event,
)
from app.db.models import ProficiencyLevel
from tests.utils.constants import (
    BAD_ID_0000, 
    PROFICIENCY_LEVEL_ID_1,
    SCHEDULE_ID_2,
    EVENT_ID_1,
    USER_ID_1,
    ROLE_ID_1,
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
def test_raise_bad_request_empty_payload():
    """Test raise bad request empty payload"""
    with pytest.raises(HTTPException) as exc_info:
        raise_bad_request_empty_payload(None)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    with pytest.raises(HTTPException) as exc_info:
        raise_bad_request_empty_payload({})
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

def test_get_or_404(get_test_db_session):
    """Test get or 404"""
    with pytest.raises(HTTPException) as exc_info:
        get_or_404(get_test_db_session, ProficiencyLevel, BAD_ID_0000)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    proficiency_level = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_1, name="Beginner", code="beginner")
    get_test_db_session.add(proficiency_level)
    get_test_db_session.commit()
    assert get_or_404(get_test_db_session, ProficiencyLevel, PROFICIENCY_LEVEL_ID_1) == proficiency_level

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

# def test_build_events_with_assignments_and_availability_from_schedule(
#     sample_schedule_with_availability,
# ):
#     """Test build_events_with_assignments_and_availability_from_schedule function"""
#     # Build events with assignments and availability from in-memory schedule
#     # Note: This test may fail if event.availability relationship doesn't exist
#     # which would indicate a bug in the helper function
#     try:
#         result = build_events_with_assignments_and_availability_from_schedule(
#             sample_schedule_with_availability
#         )
        
#         # Assertions
#         assert isinstance(result, list)
#         assert len(result) == 3  # Three events in test data
        
#         # Check first event structure
#         first_event = result[0]
#         assert first_event.event.id == EVENT_ID_1
#         assert first_event.event.schedule_id == SCHEDULE_ID_2
#         assert len(first_event.event_assignments) == 2
#         # Availability should be a list
#         assert isinstance(first_event.availability, list)
#         assert len(first_event.availability) == 2  # Two unavailable periods
        
#         # Check availability structure
#         first_availability = first_event.availability[0]
#         assert hasattr(first_availability, 'user_first_name')
#         assert hasattr(first_availability, 'user_last_name')
#         assert first_availability.user_first_name in ["Alice", "Bob"]
#         assert first_availability.user_last_name in ["Smith", "Jones"]
        
#         # Other events should have empty availability
#         assert len(result[1].availability) == 0
#         assert len(result[2].availability) == 0
#     except AttributeError as e:
#         if "'Event' object has no attribute 'availability'" in str(e):
#             pytest.fail(
#                 "event.availability relationship does not exist in Event model. "
#                 "The helper function build_events_with_assignments_and_availability_from_schedule "
#                 "references a relationship that needs to be defined."
#             )
#         else:
#             raise