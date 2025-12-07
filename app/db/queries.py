from datetime import date
from asyncpg import Connection
from app.utils.helpers import table_id, convert_id_for_table

async def fetch_all(conn: Connection, table: str) -> list[dict]:
    query = f"SELECT * FROM {table};"
    rows = await conn.fetch(query)
    return [dict(row) for row in rows]

async def fetch_one(conn: Connection, table: str, id: str | date) -> dict | None:
    id = convert_id_for_table(table, id)
    query = f"SELECT * FROM {table} WHERE {table_id(table)} = $1;"
    row = await conn.fetchrow(query, id)
    return dict(row) if row else None

async def delete_one(conn: Connection, table: str, id: str | date) -> dict | None:
    id = convert_id_for_table(table, id)
    query = f"DELETE FROM {table} WHERE {table_id(table)} = $1 RETURNING *;"
    row = await conn.fetchrow(query, id)
    return dict(row) if row else None