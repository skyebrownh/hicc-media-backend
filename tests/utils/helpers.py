from fastapi import status, Response

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
    filtered_response = {k: v for k, v in response_json.items() if k not in ("created_at", "updated_at")}
    assert filtered_response == expected_item