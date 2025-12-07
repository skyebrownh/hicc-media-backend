from datetime import date
from asyncpg import Connection
from app.utils.helpers import table_id

async def fetch_all(conn: Connection, table: str) -> list[dict]:
    query = f"SELECT * FROM {table};"
    rows = await conn.fetch(query)
    return [dict(row) for row in rows]

async def fetch_one(conn: Connection, table: str, id: str | date) -> dict | None:
    # Convert id to a date object if the table is 'dates' and id is a string
    if table == "dates" and isinstance(id, str):
        id = date.fromisoformat(id)  # Convert ISO string to date object

    query = f"SELECT * FROM {table} WHERE {table_id(table)} = $1;"
    row = await conn.fetchrow(query, id)
    return dict(row) if row else None