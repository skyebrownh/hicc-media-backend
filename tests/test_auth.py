import pytest
import pytest_asyncio
from fastapi import status, Request
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db_connection
from app.settings import settings


@pytest_asyncio.fixture
async def auth_setup(test_db_pool):
    """Set up app state and dependency override for auth tests"""
    app.state.db_pool = test_db_pool
    
    async def get_test_db_connection(request: Request):
        async with test_db_pool.acquire() as conn:
            yield conn
    
    app.dependency_overrides[get_db_connection] = get_test_db_connection
    
    yield
    
    # Clean up
    app.dependency_overrides.clear()


def create_auth_client(headers=None):
    """Helper to create an AsyncClient with custom headers"""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test", headers=headers or {})


@pytest.mark.asyncio
async def test_health_endpoint_with_auth(auth_setup):
    """Test /health endpoint with valid API key"""
    headers = {"x-api-key": settings.fast_api_key}
    
    async with create_auth_client(headers) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.asyncio
async def test_health_endpoint_without_auth(auth_setup):
    """Test /health endpoint without API key (should return 401)"""
    async with create_auth_client() as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_api_key(auth_setup):
    """Test that any endpoint returns 401 when API key is invalid"""
    headers = {"x-api-key": "invalid-key"}
    
    async with create_auth_client(headers) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"]

        # Test various endpoints
        response1 = await client.get("/users")
        assert response1.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response1.json()["detail"]
        
        response2 = await client.get("/teams")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_unauthorized_missing_api_key(auth_setup):
    """Test that any endpoint returns 401 when API key is missing"""
    async with create_auth_client() as client:
        # Test various endpoints
        response1 = await client.get("/users")
        assert response1.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response1.json()["detail"]
        
        response2 = await client.get("/teams")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response2.json()["detail"]
        
        response3 = await client.post("/users", json={"first_name": "Test", "last_name": "User"})
        assert response3.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response3.json()["detail"]


@pytest.mark.asyncio
async def test_unauthorized_empty_api_key(auth_setup):
    """Test that empty API key returns 401"""
    headers = {"x-api-key": ""}
    
    async with create_auth_client(headers) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unauthorized_whitespace_api_key(auth_setup):
    """Test that whitespace-only API key returns 401"""
    headers = {"x-api-key": "   "}
    
    async with create_auth_client(headers) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"]
