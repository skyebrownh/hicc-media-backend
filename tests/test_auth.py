import pytest
from fastapi import status
from app.settings import settings

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "async_client,expected_status,expected_response",
    [
        ({"x-api-key": settings.fast_api_key}, status.HTTP_200_OK, {"status": "ok", "database": "ok"}),
        ({}, status.HTTP_401_UNAUTHORIZED, None),  # Missing API key
        ({"x-api-key": "invalid-key"}, status.HTTP_401_UNAUTHORIZED, None),  # Invalid API key
        ({"x-api-key": ""}, status.HTTP_401_UNAUTHORIZED, None),  # Empty API key
        ({"x-api-key": "   "}, status.HTTP_401_UNAUTHORIZED, None),  # Whitespace-only API key
    ],
    indirect=["async_client"],
    ids=["valid_api_key", "missing_api_key", "invalid_api_key", "empty_api_key", "whitespace_api_key"],
)
async def test_health_endpoint_auth_scenarios(async_client, expected_status, expected_response):
    """Test /health endpoint with various authentication scenarios"""
    response = await async_client.get("/health")
    assert response.status_code == expected_status
    
    if expected_response:
        assert response.json() == expected_response
    else:
        assert "Unauthorized" in response.json()["detail"]