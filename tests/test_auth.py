import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db_pool
from app.settings import settings


@pytest.mark.asyncio
async def test_health_endpoint_with_auth(test_db_pool):
    """Test /health endpoint with valid API key"""
    headers = {"x-api-key": settings.fast_api_key}
    app.dependency_overrides[get_db_pool] = lambda: test_db_pool
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_endpoint_without_auth(test_db_pool):
    """Test /health endpoint without API key (should return 401)"""
    app.dependency_overrides[get_db_pool] = lambda: test_db_pool
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_api_key(test_db_pool):
    """Test that any endpoint returns 401 when API key is invalid"""
    headers = {"x-api-key": "invalid-key"}
    app.dependency_overrides[get_db_pool] = lambda: test_db_pool
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
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
async def test_unauthorized_missing_api_key(test_db_pool):
    """Test that any endpoint returns 401 when API key is missing"""
    app.dependency_overrides[get_db_pool] = lambda: test_db_pool
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
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
async def test_unauthorized_empty_api_key(test_db_pool):
    """Test that empty API key returns 401"""
    headers = {"x-api-key": ""}
    app.dependency_overrides[get_db_pool] = lambda: test_db_pool
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unauthorized_whitespace_api_key(test_db_pool):
    """Test that whitespace-only API key returns 401"""
    headers = {"x-api-key": "   "}
    app.dependency_overrides[get_db_pool] = lambda: test_db_pool
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"]
