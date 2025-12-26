import pytest
from fastapi import HTTPException, status
from app.utils.helpers import VALID_TABLES, validate_table_name, maybe, raise_bad_request_empty_payload, get_or_404
from app.db.models import ProficiencyLevel
from tests.utils.constants import BAD_ID_0000, PROFICIENCY_LEVEL_ID_1

def test_validate_table_name():
    """Test table name validation against whitelist"""
    # Test valid table names
    for table in VALID_TABLES:
        # Should not raise any exception
        validate_table_name(table)
    
    # Test invalid table names
    invalid_tables = [
        "invalid_table",
        "user",  # singular form not in whitelist
        "DROP TABLE users;--",  # SQL injection attempt
        "users; DELETE FROM users;--",  # SQL injection attempt
        "user_roles_old",  # similar but not exact match
        "",  # empty string
    ]
    for table in invalid_tables:
        with pytest.raises(ValueError) as exc_info:
            validate_table_name(table)
        assert "Invalid table name" in str(exc_info.value)
        assert table in str(exc_info.value)

def test_maybe():
    class TestClass:
        def __init__(self, name: str):
            self.name = name

    test_obj = TestClass("test")
    """Test maybe function"""
    assert maybe(None, "name") is None
    assert maybe(test_obj, "name") == "test"
    assert maybe(test_obj, "age") is None

def test_raise_bad_request_empty_payload():
    """Test raise bad request empty payload"""
    with pytest.raises(HTTPException) as exc_info:
        raise_bad_request_empty_payload(None)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    with pytest.raises(HTTPException) as exc_info:
        raise_bad_request_empty_payload({})
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

def test_get_or_404(get_test_db_session):
    """Test get or 404"""
    with pytest.raises(HTTPException) as exc_info:
        get_or_404(get_test_db_session, ProficiencyLevel, BAD_ID_0000)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    proficiency_level = ProficiencyLevel(id=PROFICIENCY_LEVEL_ID_1, name="Beginner", code="beginner")
    get_test_db_session.add(proficiency_level)
    get_test_db_session.commit()
    assert get_or_404(get_test_db_session, ProficiencyLevel, PROFICIENCY_LEVEL_ID_1) == proficiency_level