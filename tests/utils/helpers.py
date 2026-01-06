import json
from fastapi import status, Response
from datetime import datetime, timezone

def assert_empty_list_200(response: Response) -> None:
    """Assert that a response is an empty list and returns a 200 OK status code."""
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0
    assert response.json() == []
    
def assert_list_200(response: Response, expected_length: int) -> None:
    """Assert that a response is a list and returns a 200 OK status code."""
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == expected_length

def _filter_timestamp_keys(data, additional_keys_to_exclude=None):
    """Recursively filter out specified keys from dictionaries and lists at any nesting level."""
    keys_to_exclude = ["created_at", "updated_at", "starts_at", "ends_at"]
    if additional_keys_to_exclude is not None:
        keys_to_exclude.extend(additional_keys_to_exclude)
    
    if isinstance(data, dict):
        return {
            k: _filter_timestamp_keys(v, keys_to_exclude)
            for k, v in data.items()
            if k not in keys_to_exclude
        }
    elif isinstance(data, list):
        return [_filter_timestamp_keys(item, keys_to_exclude) for item in data]
    else:
        return data

def assert_single_item_200(response: Response, expected_item: dict) -> None:
    """Assert that a response is a single item and returns a 200 OK status code."""
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    filtered_response = _filter_timestamp_keys(response_json)
    print(json.dumps(find_dict_difference(filtered_response, expected_item), indent=4))
    assert filtered_response == expected_item

def assert_single_item_201(response: Response, expected_item: dict) -> None:
    """Assert that a response is a single item and returns a 201 CREATED status code."""
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["id"] is not None
    filtered_response = _filter_timestamp_keys(response_json, additional_keys_to_exclude=["id"])
    print(json.dumps(find_dict_difference(filtered_response, expected_item), indent=4))
    assert filtered_response == expected_item

def find_dict_difference(dict1: dict, dict2: dict) -> dict:
    """Find the difference between two dictionaries, handling nested objects and arrays.
    
    Returns only value mismatches and missing keys at any nesting level.
    Missing keys are indicated by empty structures ({} or []) on one side.
    """
    diff = {
        "dict1": {},
        "dict2": {},
    }
    
    def _compare_values(val1, val2):
        """Recursively compare two values and return their differences."""
        # Handle None values
        if val1 is None and val2 is None:
            return None, None
        if val1 is None or val2 is None:
            return val1, val2
        
        # Handle dictionaries recursively
        if isinstance(val1, dict) and isinstance(val2, dict):
            return _compare_dicts(val1, val2)
        # Handle lists/arrays - compare element by element
        elif isinstance(val1, list) and isinstance(val2, list):
            return _compare_lists(val1, val2)
        # Handle type mismatches
        elif type(val1) != type(val2):
            return val1, val2
        # Handle primitive values
        else:
            return (val1, val2) if val1 != val2 else (None, None)
    
    def _compare_lists(list1, list2):
        """Compare two lists element by element and return only differences."""
        # If lengths differ, return the entire lists as difference
        if len(list1) != len(list2):
            return list1, list2
        
        # Compare element by element
        result1 = []
        result2 = []
        has_differences = False
        
        for item1, item2 in zip(list1, list2):
            diff1, diff2 = _compare_values(item1, item2)
            if diff1 is not None or diff2 is not None:
                has_differences = True
                # Preserve pairing: always include both sides, using empty dict/list if no diff
                if diff1 is not None:
                    result1.append(diff1)
                else:
                    # No differences from dict1 side, use empty structure matching the type
                    result1.append({} if isinstance(item1, dict) else [])
                
                if diff2 is not None:
                    result2.append(diff2)
                else:
                    # No differences from dict2 side, use empty structure matching the type
                    result2.append({} if isinstance(item2, dict) else [])
        
        if not has_differences:
            return None, None
        
        return result1, result2
    
    def _compare_dicts(d1: dict, d2: dict):
        """Recursively compare two dictionaries and return nested diff structure."""
        result1 = {}
        result2 = {}
        all_keys = set(d1.keys()) | set(d2.keys())
        has_differences = False
        
        for key in all_keys:
            if key not in d1:
                # Key missing in dict1 - show empty structure on dict1 side, full value on dict2 side
                result1[key] = {}
                result2[key] = _deep_copy(d2[key])
                has_differences = True
            elif key not in d2:
                # Key missing in dict2 - show full value on dict1 side, empty structure on dict2 side
                result1[key] = _deep_copy(d1[key])
                result2[key] = {}
                has_differences = True
            else:
                # Key exists in both, compare values
                diff1, diff2 = _compare_values(d1[key], d2[key])
                if diff1 is not None or diff2 is not None:
                    has_differences = True
                    # Always include both sides to preserve pairing
                    # Use empty dict/list if one side has no differences
                    if diff1 is not None:
                        result1[key] = diff1
                    else:
                        # No differences from dict1 side, use empty structure matching the type
                        result1[key] = {} if isinstance(d1[key], dict) else ([] if isinstance(d1[key], list) else None)
                    
                    if diff2 is not None:
                        result2[key] = diff2
                    else:
                        # No differences from dict2 side, use empty structure matching the type
                        result2[key] = {} if isinstance(d2[key], dict) else ([] if isinstance(d2[key], list) else None)
        
        if not has_differences:
            return None, None
        
        # Return dicts even if empty to preserve structure when one side has differences
        return result1, result2
    
    def _deep_copy(value):
        """Create a deep copy of a value (handles dicts, lists, and primitives)."""
        if isinstance(value, dict):
            return {k: _deep_copy(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_deep_copy(item) for item in value]
        else:
            return value
    
    # Compare entire dictionaries - handles missing keys at all levels
    mismatch1, mismatch2 = _compare_dicts(dict1, dict2)
    if mismatch1 is not None:
        diff["dict1"].update(mismatch1)
    if mismatch2 is not None:
        diff["dict2"].update(mismatch2)
    
    return diff

# Parse datetimes from response and convert to UTC for comparison
# The database may return datetimes in different timezones, so we normalize to UTC
def parse_to_utc(dt_str: str) -> datetime:
    """Parse ISO datetime string and convert to UTC."""
    dt_str_normalized = dt_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(dt_str_normalized)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)