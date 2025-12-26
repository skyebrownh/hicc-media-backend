import datetime
from typing import Any
from asyncpg import Connection, Record, exceptions
from fastapi import HTTPException

# Whitelist of valid table names to prevent SQL injection
VALID_TABLES = {
    "roles",
    "proficiency_levels",
    "event_types",
    "teams",
    "users",
    "team_users",
    "user_roles",
    "schedules",
    "events",
    "event_assignments",
    "user_unavailable_periods",
}

def validate_table_name(table: str) -> None:
    """Validate that a table name is in the whitelist to prevent SQL injection."""
    if table not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}. Must be one of {sorted(VALID_TABLES)}")

def table_id(table: str) -> str:
    """Return the primary key column name for a given table."""
    if table == "dates":
        return "date"

    return f"{table[0:len(table) - 1] if table.endswith("s") else table}_id"

def maybe(value: Any, attr: str):
    """Return the value of an attribute if it is not None, otherwise return None."""
    return getattr(value, attr) if value else None

def get_date_details(date: datetime.date) -> dict:
    """Calculate and return detailed date information."""
    return {
        "calendar_year": date.year,
        "calendar_month": date.month,
        "month_name": date.strftime("%B"),
        "month_abbr": date.strftime("%b"),
        "calendar_day": date.day,
        "weekday": date.weekday(),
        "weekday_name": date.strftime("%A"),
        "is_weekend": date.weekday() >= 5,
        "is_weekday": date.weekday() < 5,
        "is_holiday": False,
        "week_number": date.isocalendar()[1],
        "is_first_of_month": date.day == 1,
        "is_last_of_month": (date + datetime.timedelta(days=1)).month != date.month,
        "calendar_quarter": (date.month - 1) // 3 + 1,
        "weekday_of_month": (date.day - 1) // 7 + 1
    }

# Helper function to build dynamic update queries
def build_update_query(
    table: str,
    id_columns: dict[str, str],
    payload: dict
) -> tuple[str, list]:
    """
    Build a parameterized SQL update query for arbitrary number of ID columns in the WHERE clause.

    Args:
        table: table name (must be in VALID_TABLES whitelist)
        id_columns: dict mapping id column name(s) to their value(s)
        payload: data to update

    Returns:
        (query, values)
    """
    validate_table_name(table)
    raise_bad_request_empty_payload(payload)

    updates = []
    values = []
    index = 1

    # SET clause
    for key, value in payload.items():
        updates.append(f"{key} = ${index}")
        values.append(value)
        index += 1

    # WHERE clause (with potentially multiple id columns)
    where_clauses = []
    for id_col, id_value in id_columns.items():
        where_clauses.append(f"{id_col} = ${index}")
        values.append(id_value)
        index += 1

    query = f"""
    UPDATE {table}
    SET {', '.join(updates)}
    WHERE {' AND '.join(where_clauses)}
    RETURNING *;
    """

    return query, values

# Helper function to build dynamic insert queries for multiple payloads
def build_insert_query(table: str, payloads: list[dict]) -> tuple[str, list]:
    """
    Build a parameterized SQL insert query for multiple rows.
    
    Args:
        table: table name (must be in VALID_TABLES whitelist)
        payloads: list of dictionaries containing data to insert
        
    Returns:
        (query, values)
    """
    validate_table_name(table)
    if not isinstance(payloads, list) or not payloads or not all(isinstance(p, dict) and p for p in payloads):
        raise_bad_request_empty_payload(payloads)

    columns = list(payloads[0].keys())
    # All payloads must have the same columns
    if any(list(p.keys()) != columns for p in payloads):
        raise ValueError("All payloads must have the same set of columns for bulk insert")

    values = []
    rows_placeholders = []
    idx = 1
    for payload in payloads:
        placeholders = [f"${i}" for i in range(idx, idx + len(columns))]
        rows_placeholders.append(f"({', '.join(placeholders)})")
        values.extend(payload.values())
        idx += len(columns)

    query = f"""
    INSERT INTO {table} ({', '.join(columns)})
    VALUES {', '.join(rows_placeholders)}
    RETURNING *;
    """
    return query, values

# Helper function to build WHERE clause from filters
def build_where_clause(table: str, filters: dict[str, str | datetime.date]) -> tuple[str, list]:
    """
    Build a WHERE clause from filter dictionary.
    
    Args:
        table: table name (must be in VALID_TABLES whitelist)
        filters: dictionary of column names to filter values
        
    Returns:
        (where_clause_string, list_of_values)
    """
    validate_table_name(table)
    if not filters:
        return "", []
    where_clauses = [f"{k} = ${i+1}" for i, k in enumerate(filters.keys())]
    clause = f" WHERE {' AND '.join(where_clauses)}"
    return clause, list(filters.values())

async def fetch_many(conn: Connection, query: str, params: list) -> Record:
    """
    Execute a query and return all matching rows.
    
    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters
        
    Returns:
        List of Record objects (empty list if no rows found)
        
    Note:
        Does not raise 404 if no rows found; returns empty list instead
    """
    return await conn.fetch(query, *params)


async def fetch_single_row(conn: Connection, query: str, params: list) -> Record:
    """
    Execute a query and return a single row, or raise HTTPException if not found.
    
    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters
        
    Returns:
        Single Record object
        
    Raises:
        HTTPException(409): If unique constraint violation occurs
        HTTPException(404): If foreign key constraint violation occurs
        HTTPException(404): If no row is found
    """
    try:
        row = await conn.fetchrow(query, *params)
    except exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=409, 
            detail="Conflict: Duplicate record"
        )
    except exceptions.ForeignKeyViolationError:
        raise HTTPException(
            status_code=404, 
            detail="Not Found: Foreign key constraint violation"
        )

    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    return row

def raise_bad_request_empty_payload(payload):
    """Validate that a payload is not empty, raising HTTPException if it is."""
    if not payload:
        raise HTTPException(status_code=400, detail="Payload cannot be empty")