import asyncpg

from fastapi import FastAPI, Request
from app.utils.env import RAILWAY_DATABASE_URL

async def connect_db(app: FastAPI):
    # Create a connection pool and store it in the app state
    app.state.db_pool = await asyncpg.create_pool(
        dsn=RAILWAY_DATABASE_URL,
        min_size=1,
        max_size=5
    )

async def close_db(app: FastAPI):
    # Close the connection pool on shutdown
    if app.state.db_pool:
        await app.state.db_pool.close()

async def get_db_pool(request: Request):
    return request.app.state.db_pool