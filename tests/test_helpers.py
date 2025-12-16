import datetime
import pytest
from fastapi import HTTPException
from app.utils.helpers import *

def test_validate_table_name():
    """Test table name validation against whitelist"""
    # Test valid table names
    valid_tables = [
        "dates", "media_roles", "proficiency_levels", "schedule_date_roles",
        "schedule_date_types", "schedule_dates", "schedules", "team_users",
        "teams", "user_dates", "user_roles", "users"
    ]
    for table in valid_tables:
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

def test_table_id():
    assert table_id("users") == "user_id"
    assert table_id("schedule_date_types") == "schedule_date_type_id"
    assert table_id("user_dates") == "user_date_id"
    assert table_id("dates") == "date"

def test_get_date_details():
    test_cases = {
        # Regular date
        "2024-06-15": {
            "calendar_year": 2024,
            "calendar_month": 6,
            "month_name": "June",
            "month_abbr": "Jun",
            "calendar_day": 15,
            "weekday": 5,
            "weekday_name": "Saturday",
            "is_weekend": True,
            "is_weekday": False,
            "is_holiday": False,
            "week_number": 24,
            "is_first_of_month": False,
            "is_last_of_month": False,
            "calendar_quarter": 2,
            "weekday_of_month": 3
        },
        # First of the month
        "2024-07-01": {
            "calendar_year": 2024,
            "calendar_month": 7,
            "month_name": "July",
            "month_abbr": "Jul",
            "calendar_day": 1,
            "weekday": 0,
            "weekday_name": "Monday",
            "is_weekend": False,
            "is_weekday": True,
            "is_holiday": False,
            "week_number": 27,
            "is_first_of_month": True,
            "is_last_of_month": False,
            "calendar_quarter": 3,
            "weekday_of_month": 1
        },
        # Last of the month
        "2024-07-31": {
            "calendar_year": 2024,
            "calendar_month": 7,
            "month_name": "July",
            "month_abbr": "Jul",
            "calendar_day": 31,
            "weekday": 2,
            "weekday_name": "Wednesday",
            "is_weekend": False,
            "is_weekday": True,
            "is_holiday": False,
            "week_number": 31,
            "is_first_of_month": False,
            "is_last_of_month": True,
            "calendar_quarter": 3,
            "weekday_of_month": 5
        },
        # 5th weekday of the month (e.g., 5th Monday)
        "2024-07-29": {
            "calendar_year": 2024,
            "calendar_month": 7,
            "month_name": "July",
            "month_abbr": "Jul",
            "calendar_day": 29,
            "weekday": 0,
            "weekday_name": "Monday",
            "is_weekend": False,
            "is_weekday": True,
            "is_holiday": False,
            "week_number": 31,
            "is_first_of_month": False,
            "is_last_of_month": False,
            "calendar_quarter": 3,
            "weekday_of_month": 5
        },
        # Leap year, February 29
        "2024-02-29": {
            "calendar_year": 2024,
            "calendar_month": 2,
            "month_name": "February",
            "month_abbr": "Feb",
            "calendar_day": 29,
            "weekday": 3,
            "weekday_name": "Thursday",
            "is_weekend": False,
            "is_weekday": True,
            "is_holiday": False,
            "week_number": 9,
            "is_first_of_month": False,
            "is_last_of_month": True,
            "calendar_quarter": 1,
            "weekday_of_month": 5
        },
    }

    for date_str, expected in test_cases.items():
        details = get_date_details(datetime.date.fromisoformat(date_str))
        for key, value in expected.items():
            assert details[key] == value, f"{date_str}: {key} expected {value}, got {details[key]}"

def test_build_update_query_invalid_table():
    """Test that invalid table name raises ValueError"""
    id_columns = {"user_id": "4843a172-52d9-4378-a766-0d342b4ce095"}
    with pytest.raises(ValueError) as exc_info:
        build_update_query("invalid_table", id_columns, {"name": "John"})
    assert "Invalid table name" in str(exc_info.value)


def test_build_update_query_empty_payload():
    """Test that empty payload triggers HTTPException"""
    table = "users"
    id_columns = {"user_id": "4843a172-52d9-4378-a766-0d342b4ce095"}
    with pytest.raises(HTTPException) as exc_info:
        build_update_query(table, id_columns, {})
    assert exc_info.value.status_code == 400
    assert "Payload cannot be empty" in str(exc_info.value.detail)


@pytest.mark.parametrize("payload,expected_set,expected_values", [
    ({"name": "John"}, "SET name = $1", ["John"]),
    ({"name": "John", "email": "john@example.com"}, "SET name = $1, email = $2", ["John", "john@example.com"]),
    ({"name": "John", "email": "john@example.com", "phone": "555-1234"}, 
     "SET name = $1, email = $2, phone = $3", ["John", "john@example.com", "555-1234"]),
])
def test_build_update_query_payloads(payload, expected_set, expected_values):
    """Test build_update_query with various payload sizes"""
    table = "users"
    id_columns = {"user_id": "4843a172-52d9-4378-a766-0d342b4ce095"}
    user_id = "4843a172-52d9-4378-a766-0d342b4ce095"
    
    query, values = build_update_query(table, id_columns, payload)
    
    assert "UPDATE users" in query
    assert expected_set in query
    assert f"WHERE user_id = ${len(payload) + 1}" in query
    assert values == expected_values + [user_id]

def test_build_insert_query_invalid_table():
    """Test that invalid table name raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        build_insert_query("invalid_table", [{"name": "Jane"}])
    assert "Invalid table name" in str(exc_info.value)


def test_build_insert_query_empty_payload():
    """Test that empty payload triggers HTTPException"""
    table = "users"
    with pytest.raises(HTTPException) as exc_info:
        build_insert_query(table, [])
    assert exc_info.value.status_code == 400
    assert "Payload cannot be empty" in str(exc_info.value.detail)


@pytest.mark.parametrize("payload,expected_columns,expected_values", [
    ([{"name": "Jane"}], "(name)", ["Jane"]),
    ([{"name": "Jane", "email": "jane@example.com"}], "(name, email)", ["Jane", "jane@example.com"]),
    ([{"name": "Jane", "email": "jane@example.com", "phone": "555-5678"}], 
     "(name, email, phone)", ["Jane", "jane@example.com", "555-5678"]),
])
def test_build_insert_query_single_row(payload, expected_columns, expected_values):
    """Test build_insert_query with single row payloads of various sizes"""
    table = "users"
    query, values = build_insert_query(table, payload)
    
    assert "INSERT INTO users" in query
    assert expected_columns in query
    assert f"VALUES ({', '.join(f'${i+1}' for i in range(len(expected_values)))})" in query
    assert values == expected_values


def test_build_insert_query_bulk():
    """Test bulk insert with multiple rows"""
    table = "users"
    payload = [
        {"name": "Jane", "email": "jane@example.com", "phone": "555-5678"},
        {"name": "Alice", "email": "alice@example.com", "phone": "555-8888"}
    ]
    query, values = build_insert_query(table, payload)
    
    assert "INSERT INTO users" in query
    assert "(name, email, phone)" in query
    assert "VALUES ($1, $2, $3), ($4, $5, $6)" in query
    assert values == [
        "Jane", "jane@example.com", "555-5678",
        "Alice", "alice@example.com", "555-8888"
    ]


@pytest.mark.parametrize("payload,description", [
    ([
        {"name": "Jane", "email": "jane@example.com", "phone": "555-5678"},
        {"name": "Alice", "email": "alice@example.com"}  # Missing "phone"
    ], "missing column"),
    ([
        {"name": "Jane", "email": "jane@example.com"},
        {"phone": "555-8888", "address": "123 Main St"}  # Completely different columns
    ], "different columns"),
])
def test_build_insert_query_invalid_bulk_payloads(payload, description):
    """Test that bulk insert with mismatched columns raises ValueError"""
    table = "users"
    with pytest.raises(ValueError) as exc_info:
        build_insert_query(table, payload)
    assert "All payloads must have the same set of columns for bulk insert" in str(exc_info.value)

def test_build_where_clause_invalid_table():
    """Test that invalid table name raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        build_where_clause("invalid_table", {"user_id": "123"})
    assert "Invalid table name" in str(exc_info.value)
    

def test_build_where_clause_empty_filters():
    """Test build_where_clause with empty filters"""
    table = "users"
    clause, values = build_where_clause(table, {})
    assert clause == ""
    assert values == []


@pytest.mark.parametrize("filters,expected_clause_pattern,expected_values", [
    ({"user_id": "123"}, "WHERE user_id = $1", ["123"]),
    ({"user_id": "123", "is_active": True}, "WHERE user_id = $1 AND is_active = $2", ["123", True]),
    ({"user_id": "123", "is_active": True, "email": "test@example.com"}, 
     "WHERE user_id = $1 AND is_active = $2 AND email = $3", ["123", True, "test@example.com"]),
])
def test_build_where_clause_filters(filters, expected_clause_pattern, expected_values):
    """Test build_where_clause with various filter combinations"""
    table = "users"
    clause, values = build_where_clause(table, filters)
    assert expected_clause_pattern in clause
    assert values == expected_values


def test_build_where_clause_with_date():
    """Test build_where_clause with date filter"""
    test_date = datetime.date(2024, 1, 1)
    clause, values = build_where_clause("dates", {"date": test_date})
    assert "WHERE date = $1" in clause
    assert values == [test_date]


def test_build_where_clause_with_none_value():
    """Test build_where_clause with None value (should use = operator, not IS NULL)"""
    table = "users"
    clause, values = build_where_clause(table, {"email": None})
    # Current implementation uses = operator even for None
    assert "WHERE email = $1" in clause
    assert values == [None]


def test_build_where_clause_with_multiple_none_values():
    """Test build_where_clause with multiple None values"""
    table = "users"
    clause, values = build_where_clause(table, {"email": None, "phone": None})
    assert "WHERE email = $1 AND phone = $2" in clause
    assert values == [None, None]


def test_build_where_clause_with_list_value():
    """Test build_where_clause with list value (should use = operator, not IN)"""
    table = "users"
    clause, values = build_where_clause(table, {"user_id": ["123", "456", "789"]})
    # Current implementation uses = operator even for lists
    assert "WHERE user_id = $1" in clause
    assert values == [["123", "456", "789"]]
    

def test_build_where_clause_with_mixed_types():
    """Test build_where_clause with mixed value types including None and list"""
    table = "users"
    test_date = datetime.date(2024, 1, 1)
    filters = {
        "user_id": "123",
        "email": None,
        "is_active": True,
        "created_date": test_date,
        "tags": ["tag1", "tag2"]
    }
    clause, values = build_where_clause(table, filters)
    assert "WHERE user_id = $1 AND email = $2 AND is_active = $3 AND created_date = $4 AND tags = $5" in clause
    assert values == ["123", None, True, test_date, ["tag1", "tag2"]]
