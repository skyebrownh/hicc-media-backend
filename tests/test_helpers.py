import pytest
from fastapi import HTTPException, status

from app.utils.helpers import raise_exception_if_not_found, require_non_empty_payload
from app.db.models import ProficiencyLevel, Role, RoleUpdate
from tests.utils.constants import PROFICIENCY_LEVEL_ID_1

# =============================
# TESTS
# =============================
def test_raise_exception_if_not_found():
    """Test raise_exception_if_not_found function"""
    # Test: raises 404 when object is None with default status code
    with pytest.raises(HTTPException) as exc_info:
        raise_exception_if_not_found(None, ProficiencyLevel)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "ProficiencyLevel not found"

    # Test: raises custom status code when object is None
    with pytest.raises(HTTPException) as exc_info:
        raise_exception_if_not_found(None, Role, http_status_code=status.HTTP_400_BAD_REQUEST)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Role not found"

    # Test: does nothing when object exists
    proficiency_level = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_1, name="Beginner", code="beginner")
    raise_exception_if_not_found(proficiency_level, ProficiencyLevel)
    assert str(proficiency_level.id) == str(PROFICIENCY_LEVEL_ID_1)

def test_require_non_empty_payload():
    """Test require_non_empty_payload function"""
    # Test: raises 400 when payload is empty (all fields unset)
    with pytest.raises(HTTPException) as exc_info:
        require_non_empty_payload(RoleUpdate())
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Empty payload is not allowed."

    # Test: returns dict when payload has at least one field set
    payload = RoleUpdate(name="Test Role")
    result = require_non_empty_payload(payload)
    assert isinstance(result, dict)
    assert result == {"name": "Test Role"}

    # Test: returns dict with only set fields (excludes unset fields)
    payload = RoleUpdate(name="Test Role", description="Test Description")
    result = require_non_empty_payload(payload)
    assert result == {"name": "Test Role", "description": "Test Description"}
    assert "order" not in result
    assert "is_active" not in result

    # Test: returns dict with single field set
    payload = RoleUpdate(is_active=False)
    result = require_non_empty_payload(payload)
    assert result == {"is_active": False}