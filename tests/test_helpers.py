import datetime
import pytest
from fastapi import HTTPException
from app.utils.helpers import *

def test_table_id():
    assert table_id("users") == "user_id"
    assert table_id("schedule_date_types") == "schedule_date_type_id"
    assert table_id("user_availability") == "user_availability_id"
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

def test_build_update_query():
    table = "users"
    id_column = "user_id"
    id_value = "4843a172-52d9-4378-a766-0d342b4ce095"

    # Test empty payload triggers HTTPException (bad request)
    with pytest.raises(HTTPException) as exc_info:
        build_update_query(table, id_column, id_value, {})
    assert exc_info.value.status_code == 400
    assert "Payload cannot be empty" in str(exc_info.value.detail)

    # Test single-field payload
    payload1 = {"name": "John"}
    query1, values1 = build_update_query(table, id_column, id_value, payload1)
    assert "UPDATE users" in query1
    assert "SET name = $1" in query1
    assert "WHERE user_id = $2" in query1
    assert values1 == ["John", "4843a172-52d9-4378-a766-0d342b4ce095"]

    # Test two-field payload
    payload2 = {"name": "John", "email": "john@example.com"}
    query2, values2 = build_update_query(table, id_column, id_value, payload2)
    assert "UPDATE users" in query2
    assert "SET name = $1, email = $2" in query2
    assert "WHERE user_id = $3" in query2
    assert values2 == ["John", "john@example.com", "4843a172-52d9-4378-a766-0d342b4ce095"]

    # Test three-field payload
    payload3 = {"name": "John", "email": "john@example.com", "phone": "555-1234"}
    query3, values3 = build_update_query(table, id_column, id_value, payload3)
    assert "UPDATE users" in query3
    assert "SET name = $1, email = $2, phone = $3" in query3
    assert "WHERE user_id = $4" in query3
    assert values3 == ["John", "john@example.com", "555-1234", "4843a172-52d9-4378-a766-0d342b4ce095"]

def test_build_insert_query():
    table = "users"

    # Test empty payload triggers HTTPException (bad request)
    with pytest.raises(HTTPException) as exc_info:
        build_insert_query(table, {})
    assert exc_info.value.status_code == 400
    assert "Payload cannot be empty" in str(exc_info.value.detail)

    # Test single-field payload
    payload1 = {"name": "Jane"}
    query1, values1 = build_insert_query(table, payload1)
    assert "INSERT INTO users" in query1
    assert "(name)" in query1
    assert "VALUES ($1)" in query1
    assert values1 == ["Jane"]

    # Test two-field payload
    payload2 = {"name": "Jane", "email": "jane@example.com"}
    query2, values2 = build_insert_query(table, payload2)
    assert "INSERT INTO users" in query2
    assert "(name, email)" in query2
    assert "VALUES ($1, $2)" in query2
    assert values2 == ["Jane", "jane@example.com"]

    # Test three-field payload
    payload3 = {"name": "Jane", "email": "jane@example.com", "phone": "555-5678"}
    query3, values3 = build_insert_query(table, payload3)
    assert "INSERT INTO users" in query3
    assert "(name, email, phone)" in query3
    assert "VALUES ($1, $2, $3)" in query3
    assert values3 == ["Jane", "jane@example.com", "555-5678"]