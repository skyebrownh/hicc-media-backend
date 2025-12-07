from asyncpg import Connection

async def fetch_all(conn: Connection, table: str) -> list[dict]:
    query = f"SELECT * FROM {table};"
    rows = await conn.fetch(query)
    return [dict(row) for row in rows]

async def fetch_one(conn: Connection, table: str, id: str) -> dict | None:
    query = f"SELECT * FROM {table} WHERE user_id = $1;"
    row = await conn.fetchrow(query, id)
    return dict(row) if row else None