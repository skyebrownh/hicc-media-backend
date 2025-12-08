import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils.supabase import SupabaseService
from .helpers import SUPABASE_TEST_URL, SUPABASE_TEST_API_KEY, FAST_API_KEY
from app.utils.dependencies import get_supabase_service 

__all__ = [
    "supabase_service",
    "test_client"
]

@pytest.fixture(scope="session")
def supabase_service():
    return SupabaseService(url=SUPABASE_TEST_URL, key=SUPABASE_TEST_API_KEY)

@pytest.fixture
def test_client(supabase_service):
    headers = {"x-api-key": FAST_API_KEY}
    app.dependency_overrides[get_supabase_service] = lambda: supabase_service
    with TestClient(app) as client:
        client.headers.update(headers)
        yield client
    app.dependency_overrides = {} # cleans state after test