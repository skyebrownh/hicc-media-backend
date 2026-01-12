from app.services.builders import build_events_with_assignments_from_schedule, build_events_with_assignments_from_event
from tests.utils.constants import EVENT_ID_1, SCHEDULE_ID_2, EVENT_TYPE_ID_1, EVENT_ASSIGNMENT_ID_1, ROLE_ID_1, USER_ID_1

def test_build_events_with_assignments_from_schedule(sample_schedule_with_events):
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