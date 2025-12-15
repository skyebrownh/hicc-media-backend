import pytest
import pytest_asyncio
from fastapi import status
from tests.utils.helpers import assert_empty_list_200, insert_media_roles

MEDIA_ROLE_ID_1 = "58a6929c-f40d-4363-984c-4c221f41d4f0"
MEDIA_ROLE_ID_2 = "fb4d832f-6a45-473e-b9e2-c0495938d005"
MEDIA_ROLE_ID_3 = "c4b13e8c-45e9-49d6-8bf3-2f2fbb4404b1"
MEDIA_ROLE_ID_4 = "e1fdfd00-e097-415b-c3c7-9579c4c1bb44"

# =============================
# HELPER FIXTURES
# =============================
@pytest_asyncio.fixture
async def seed_media_roles_helper(test_db_pool):
    """Helper fixture to seed media roles in the database"""
    async def seed_media_roles(media_roles: list[dict]):
        async with test_db_pool.acquire() as conn:
            await conn.execute(insert_media_roles(media_roles))
    return seed_media_roles

# =============================
# GET ALL MEDIA ROLES
# =============================
@pytest.mark.asyncio
async def test_get_all_media_roles_none_exist(async_client):
    """Test when no media roles exist returns empty list"""
    response = await async_client.get("/media_roles")
    assert_empty_list_200(response)


@pytest.mark.asyncio
async def test_get_all_media_roles_success(async_client, seed_media_roles_helper):
    """Test getting all media roles after inserting a variety"""
    media_roles = [
        {"media_role_name": "Role 1", "sort_order": 1, "media_role_code": "role_1"},
        {"media_role_name": "Role 2", "sort_order": 2, "media_role_code": "role_2"},
        {"media_role_name": "Role 3", "sort_order": 3, "media_role_code": "role_3"},
    ]
    await seed_media_roles_helper(media_roles)

    response = await async_client.get("/media_roles")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert response_json[0]["media_role_name"] == "Role 1"
    assert response_json[1]["media_role_id"] is not None
    assert response_json[1]["media_role_code"] == "role_2"
    assert response_json[2]["description"] is None
    assert response_json[2]["is_active"] is True

# =============================
# GET SINGLE MEDIA ROLE
# =============================
@pytest.mark.parametrize("seed_roles, media_role_id, expected_status", [
    # No media roles in DB
    ([], MEDIA_ROLE_ID_1, status.HTTP_404_NOT_FOUND),
    # Media role not present
    (
        [{"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "Role 1", "description": "description 1", "sort_order": 1, "media_role_code": "role_1"}],
        "00000000-0000-0000-0000-000000000000",
        status.HTTP_404_NOT_FOUND
    ),
    # Invalid UUID format
    ([], "invalid-uuid-format", status.HTTP_422_UNPROCESSABLE_CONTENT),
])
@pytest.mark.asyncio
async def test_get_single_media_role_error_cases(async_client, seed_media_roles_helper, seed_roles, media_role_id, expected_status):
    """Test GET single media role error cases (404 and 422)"""
    # Optionally seed DB
    if seed_roles:
        await seed_media_roles_helper(seed_roles)
    response = await async_client.get(f"/media_roles/{media_role_id}")
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_get_single_media_role_success(async_client, seed_media_roles_helper):
    """Test GET single media role success case"""
    media_roles = [
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Role 2", "description": "description 2", "sort_order": 2, "media_role_code": "role_2"},
    ]
    await seed_media_roles_helper(media_roles)
    
    response = await async_client.get(f"/media_roles/{MEDIA_ROLE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["media_role_name"] == "Role 2"
    assert response_json["media_role_code"] == "role_2"
    assert response_json["description"] == "description 2"
    assert response_json["is_active"] is True

# =============================
# INSERT MEDIA ROLE
# =============================
@pytest.mark.parametrize("seed_roles, payload, expected_status", [
    # empty payload
    ([], {}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # missing required fields
    ([], {"media_role_name": "Incomplete Role"}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # invalid data types
    ([], {"media_role_name": "Bad Role", "sort_order": "not_an_int", "media_role_code": 12345}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    # duplicate media_role_code (after inserting new_role successfully, trying again should fail)
    (
        [{"media_role_id": MEDIA_ROLE_ID_4, "media_role_name": "New Role", "sort_order": 4, "media_role_code": "new_role"}],
        {"media_role_name": "Duplicate Code", "sort_order": 6, "media_role_code": "new_role"},
        status.HTTP_409_CONFLICT
    ),
    # media_role_id not allowed in payload
    (
        [{"media_role_id": MEDIA_ROLE_ID_4, "media_role_name": "Another Role", "sort_order": 5, "media_role_code": "another_role"}],
        {"media_role_id": MEDIA_ROLE_ID_4, "media_role_name": "Duplicate ID Role", "sort_order": 7, "media_role_code": "duplicate_id_role"},
        status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
])
@pytest.mark.asyncio
async def test_insert_media_role_error_cases(async_client, seed_media_roles_helper, seed_roles, payload, expected_status):
    """Test INSERT media role error cases (422 and 409)"""
    # Optionally seed DB
    if seed_roles:
        await seed_media_roles_helper(seed_roles)
    
    response = await async_client.post("/media_roles", json=payload)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_insert_media_role_success(async_client):
    """Test valid media role insertion"""
    good_payload = {
        "media_role_name": "New Role",
        "sort_order": 4,
        "media_role_code": "new_role"
    }
    
    response = await async_client.post("/media_roles", json=good_payload)
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["media_role_id"] is not None
    assert response_json["media_role_name"] == "New Role"
    assert response_json["media_role_code"] == "new_role"
    assert response_json["is_active"] is True

# =============================
# UPDATE MEDIA ROLE
# =============================
@pytest.mark.parametrize("seed_roles, media_role_path, payload, expected_status", [
    # media role not found
    (
        [{"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "Role 1", "description": "description 1", "sort_order": 1, "media_role_code": "role_1"}],
        "/media_roles/00000000-0000-0000-0000-000000000000",
        {"media_role_name": "Updated Role Name", "description": "Updated description", "sort_order": 100, "is_active": False},
        status.HTTP_404_NOT_FOUND
    ),
    # invalid UUID format
    (
        [{"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "Role 1", "description": "description 1", "sort_order": 1, "media_role_code": "role_1"}],
        "/media_roles/invalid-uuid-format",
        {"media_role_name": "Updated Role Name", "description": "Updated description", "sort_order": 100, "is_active": False},
        status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
    # empty payload
    (
        [{"media_role_id": MEDIA_ROLE_ID_3, "media_role_name": "Role 3", "description": "description 3", "sort_order": 3, "media_role_code": "role_3"}],
        f"/media_roles/{MEDIA_ROLE_ID_3}",
        {},
        status.HTTP_400_BAD_REQUEST
    ),
    # invalid data types
    (
        [{"media_role_id": MEDIA_ROLE_ID_3, "media_role_name": "Role 3", "description": "description 3", "sort_order": 3, "media_role_code": "role_3"}],
        f"/media_roles/{MEDIA_ROLE_ID_3}",
        {"media_role_name": 12345},
        status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
    # non-updatable field
    (
        [{"media_role_id": MEDIA_ROLE_ID_3, "media_role_name": "Role 3", "description": "description 3", "sort_order": 3, "media_role_code": "role_3"}],
        f"/media_roles/{MEDIA_ROLE_ID_3}",
        {"media_role_name": "Invalid", "media_role_code": "invalid"},
        status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
])
@pytest.mark.asyncio
async def test_update_media_role_error_cases(async_client, seed_media_roles_helper, seed_roles, media_role_path, payload, expected_status):
    """Test UPDATE media role error cases (400, 404, and 422)"""
    # Seed media role data
    await seed_media_roles_helper(seed_roles)
    
    response = await async_client.patch(media_role_path, json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize("media_role_id, payload, expected_fields, unchanged_fields", [
    # full update
    (
        MEDIA_ROLE_ID_3,
        {"media_role_name": "Updated Role Name", "description": "Updated description", "sort_order": 100, "is_active": False},
        {"media_role_name": "Updated Role Name", "description": "Updated description", "is_active": False},
        {"media_role_code": "role_3"}
    ),
    # partial update (is_active only)
    (
        MEDIA_ROLE_ID_2,
        {"is_active": False},
        {"is_active": False},
        {"media_role_name": "Role 2", "description": "description 2", "media_role_code": "role_2"}
    ),
    # partial update (media_role_name only)
    (
        MEDIA_ROLE_ID_1,
        {"media_role_name": "Partially Updated Role"},
        {"media_role_name": "Partially Updated Role"},
        {"description": "description 1", "media_role_code": "role_1", "is_active": True}
    ),
])
@pytest.mark.asyncio
async def test_update_media_role_success(async_client, seed_media_roles_helper, media_role_id, payload, expected_fields, unchanged_fields):
    """Test valid media role updates"""
    # Seed media role data
    media_roles = [
        {"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "Role 1", "description": "description 1", "sort_order": 1, "media_role_code": "role_1"},
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Role 2", "description": "description 2", "sort_order": 2, "media_role_code": "role_2"},
        {"media_role_id": MEDIA_ROLE_ID_3, "media_role_name": "Role 3", "description": "description 3", "sort_order": 3, "media_role_code": "role_3"},
    ]
    await seed_media_roles_helper(media_roles)
    
    response = await async_client.patch(f"/media_roles/{media_role_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    for field, expected_value in expected_fields.items():
        assert response_json[field] == expected_value
    for field, expected_value in unchanged_fields.items():
        assert response_json[field] == expected_value

# =============================
# DELETE MEDIA ROLE
# =============================
@pytest.mark.parametrize("seed_roles, media_role_path, expected_status", [
    # media role not found
    (
        [{"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "Role 1", "sort_order": 1, "media_role_code": "role_1"}],
        "/media_roles/00000000-0000-0000-0000-000000000000",
        status.HTTP_404_NOT_FOUND
    ),
    # invalid UUID format
    (
        [{"media_role_id": MEDIA_ROLE_ID_1, "media_role_name": "Role 1", "sort_order": 1, "media_role_code": "role_1"}],
        "/media_roles/invalid-uuid-format",
        status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
])
@pytest.mark.asyncio
async def test_delete_media_role_error_cases(async_client, seed_media_roles_helper, seed_roles, media_role_path, expected_status):
    """Test DELETE media role error cases (404 and 422)"""
    # Seed media role data
    await seed_media_roles_helper(seed_roles)
    
    response = await async_client.delete(media_role_path)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_delete_media_role_success(async_client, seed_media_roles_helper):
    """Test successful media role deletion with verification"""
    # Seed media roles data directly into test DB
    media_roles = [
        {"media_role_id": MEDIA_ROLE_ID_2, "media_role_name": "Role 2", "sort_order": 2, "media_role_code": "role_2"},
    ]
    await seed_media_roles_helper(media_roles)

    # Test successful deletion
    response = await async_client.delete(f"/media_roles/{MEDIA_ROLE_ID_2}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["media_role_id"] == MEDIA_ROLE_ID_2

    # Verify deletion by trying to get it again
    verify_response = await async_client.get(f"/media_roles/{MEDIA_ROLE_ID_2}")
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND