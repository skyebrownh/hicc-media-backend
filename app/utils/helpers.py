import datetime
from asyncpg import Connection, Record
from fastapi import HTTPException

# Return the primary key column name for a given table
def table_id(table: str) -> str:
    if table == "dates":
        return "date"

    return f"{table[0:len(table) - 1] if table.endswith("s") else table}_id"

# Convert id to a date object if the table is 'dates'
def convert_id_for_table(table: str, id: str | datetime.date) -> str | datetime.date:
    if table == "dates" and isinstance(id, str):
        return datetime.date.fromisoformat(id)  # Convert ISO string to date object
    return id

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
        "week_number": int(date.strftime("%U")),
        "is_first_of_month": date.day == 1,
        "is_last_of_month": (date + datetime.timedelta(days=1)).month != date.month,
        "calendar_quarter": (date.month - 1) // 3 + 1,
        "weekday_of_month": (date.day - 1) // 7 + 1
    }

# Helper function to build dynamic update queries
def build_update_query(table: str, id_column: str, id_value: str, payload: dict) -> tuple[str, list]:
    raise_bad_request_empty_payload(payload)

    updates = []
    values = []
    index = 1

    # Build the SET clause dynamically
    for key, value in payload.items():
        updates.append(f"{key} = ${index}")
        values.append(value)
        index += 1

    values.append(id_value)  # Add the ID value for the WHERE clause

    query = f"""
    UPDATE {table}
    SET {', '.join(updates)}
    WHERE {id_column} = ${index}
    RETURNING *;
    """

    return query, values

# Helper function to build dynamic insert queries
def build_insert_query(table: str, payload: dict) -> tuple[str, list]:
    raise_bad_request_empty_payload(payload)

    columns = list(payload.keys())
    values = list(payload.values())
    placeholders = [f"${i+1}" for i in range(len(columns))]

    query = f"""
    INSERT INTO {table} ({', '.join(columns)})
    VALUES ({', '.join(placeholders)})
    RETURNING *;
    """

    return query, values

# Helper functions to fetch record or raise 404
async def fetch_or_404(conn: Connection, query: str, params: list) -> Record:
    rows = await conn.fetch(query, *params)
    if not rows:
        raise HTTPException(status_code=404, detail="Record not found")
    return rows

async def fetch_row_or_404(conn: Connection, query: str, params: list) -> Record:
    row = await conn.fetchrow(query, *params)
    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    return row

# Helper to check payload and raise Bad Request if empty
def raise_bad_request_empty_payload(payload):
    if not payload:
        raise HTTPException(status_code=400, detail="Payload cannot be empty")