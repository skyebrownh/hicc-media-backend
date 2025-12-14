import datetime
from asyncpg import Connection, Record, exceptions
from fastapi import HTTPException

# Return the primary key column name for a given table
def table_id(table: str) -> str:
    if table == "dates":
        return "date"

    return f"{table[0:len(table) - 1] if table.endswith("s") else table}_id"

# Return a dict of detailed date information
def get_date_details(date: datetime.date) -> dict:
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
        table: table name
        id_columns: dict mapping id column name(s) to their value(s)
        payload: data to update

    Returns:
        (query, values)
    """
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
        if not filters:
            return "", []
        where_clauses = [f"{k} = ${i+1}" for i, k in enumerate(filters.keys())]
        clause = f" WHERE {' AND '.join(where_clauses)}"
        return clause, list(filters.values())

# Helper functions to fetch record or raise 404
async def fetch_many(conn: Connection, query: str, params: list) -> Record:
    return await conn.fetch(query, *params)
    # Do not raise 404 if no rows found; return 200 OK with empty list instead

async def fetch_single_row(conn: Connection, query: str, params: list) -> Record:
    try:
        row = await conn.fetchrow(query, *params)
    except exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=409, 
            detail="Conflict: Duplicate record"
        )
    except exceptions.ForeignKeyViolationError:
        raise HTTPException(
            status_code=400, 
            detail="Bad Request: Foreign key constraint violation"
        )

    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    return row

# Helper to check payload and raise Bad Request if empty
def raise_bad_request_empty_payload(payload):
    if not payload:
        raise HTTPException(status_code=400, detail="Payload cannot be empty")