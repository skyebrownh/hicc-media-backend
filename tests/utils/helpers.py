from fastapi import status, Response

def assert_empty_list_200(response: Response) -> None:
    """Assert that a response is an empty list and returns a 200 OK status code."""
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0
    assert response.json() == []
    