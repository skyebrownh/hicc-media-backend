import pytest

from app.utils.helpers import raise_exception_if_not_found, require_non_empty_payload
from app.db.models import ProficiencyLevel, Role, RoleUpdate
from tests.utils.constants import PROFICIENCY_LEVEL_ID_1
from app.utils.exceptions import EmptyPayloadError, NotFoundError

# =============================
# TESTS
# =============================
def test_raise_exception_if_not_found():
    # Test: raises 404 when object is None with default status code
    with pytest.raises(NotFoundError) as exc_info:
        raise_exception_if_not_found(None, ProficiencyLevel)
    assert str(exc_info.value) == "ProficiencyLevel not found"

    # Test: raises custom status code when object is None
    with pytest.raises(NotFoundError) as exc_info:
        raise_exception_if_not_found(None, Role)
    assert str(exc_info.value) == "Role not found"

    # Test: does nothing when object exists
    proficiency_level = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_1, name="Beginner", code="beginner")
    raise_exception_if_not_found(proficiency_level, ProficiencyLevel)
    assert str(proficiency_level.id) == str(PROFICIENCY_LEVEL_ID_1)

def test_require_non_empty_payload():
    # Test: raises 400 when payload is empty (all fields unset)
    with pytest.raises(EmptyPayloadError) as exc_info:
        require_non_empty_payload(RoleUpdate())
    assert str(exc_info.value) == "Empty payload is not allowed."

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