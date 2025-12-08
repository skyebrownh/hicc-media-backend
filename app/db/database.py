import logging
import asyncpg
from fastapi import FastAPI, Request, HTTPException
from app.utils.env import RAILWAY_DATABASE_URL

logger = logging.getLogger(__name__)

async def connect_db(app: FastAPI):
    # Create a connection pool and store it in the app state
    try:
        app.state.db_pool = await asyncpg.create_pool(
            dsn=RAILWAY_DATABASE_URL,
            min_size=1,
            max_size=5
        )
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

async def close_db(app: FastAPI):
    if app.state.db_pool:
        await app.state.db_pool.close()

async def get_db_pool(request: Request):
    return request.app.state.db_pool