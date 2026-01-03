import pytest
from fastapi import HTTPException, status
from app.utils.helpers import maybe, raise_bad_request_empty_payload, get_or_404
from app.db.models import ProficiencyLevel
from tests.utils.constants import BAD_ID_0000, PROFICIENCY_LEVEL_ID_1

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