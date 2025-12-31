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

def assert_single_item_200(response: Response, expected_item: dict) -> None:
    """Assert that a response is a single item and returns a 200 OK status code."""
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    filtered_response = {k: v for k, v in response_json.items() if k not in ("created_at", "updated_at", "starts_at", "ends_at")}
    print(json.dumps(find_dict_difference(filtered_response, expected_item), indent=4))
    assert filtered_response == expected_item

def find_dict_difference(dict1: dict, dict2: dict) -> dict:
    """Find the difference between two dictionaries."""
    diff = {
        "value_mismatch": {
            "dict1": {},
            "dict2": {},
        },
        "dict1_missing_keys": {},
        "dict2_missing_keys": {},
    }
    # value mismatch
    diff["value_mismatch"]["dict1"].update({k: v for k, v in dict1.items() if v != dict2.get(k)})
    diff["value_mismatch"]["dict2"].update({k: v for k, v in dict2.items() if v != dict1.get(k)})
    # key mismatch
    diff["dict1_missing_keys"].update({k: v for k, v in dict1.items() if k not in dict2})
    diff["dict2_missing_keys"].update({k: v for k, v in dict2.items() if k not in dict1})
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