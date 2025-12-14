import logging
from typing import AsyncGenerator
import asyncpg
from fastapi import FastAPI, Request
from app.settings import settings

logger = logging.getLogger(__name__)

async def connect_db(app: FastAPI):
    """
    Create a database connection pool and store it in the app state.
    
    This is called during application startup. Raises exceptions (not HTTPException)
    so FastAPI can properly handle startup failures.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        Exception: If database connection fails (will cause application startup to fail)
    """
    try:
        app.state.db_pool = await asyncpg.create_pool(
            dsn=settings.railway_database_url,
            min_size=2,              # Keep 2 connections warm (faster response)
            max_size=10,             # Allow up to 10 concurrent connections
            max_queries=50000,        # Close connection after N queries (prevent leaks)
            max_inactive_connection_lifetime=300,  # Close idle connections after 5 min
            timeout=10,               # Wait up to 10s for connection from pool
            command_timeout=30,       # Query timeout (prevent hanging queries)
        )
        logger.info("Database connection pool created successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        # Raise the exception directly (not HTTPException) so FastAPI can handle startup failures properly
        raise

async def close_db(app: FastAPI):
    """
    Close the database connection pool during application shutdown.
    
    Args:
        app: FastAPI application instance
    """
    if app.state.db_pool:
        await app.state.db_pool.close()

async def get_db_pool(request: Request):
    """
    Dependency that provides the database connection pool.
    
    Returns:
        The asyncpg connection pool from app state
    """
    return request.app.state.db_pool


async def get_db_connection(request: Request) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Dependency that provides a database connection for each request.
    
    Each request gets its own connection from the pool. The connection is
    automatically returned to the pool when the request completes.
    This reduces boilerplate in route handlers while maintaining
    connection independence between requests.
    
    Yields:
        A database connection from the pool
    """
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        yield conn