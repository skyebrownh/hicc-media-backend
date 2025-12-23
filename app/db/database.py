import logging
from fastapi import FastAPI
from sqlmodel import create_engine
from app.settings import settings

logger = logging.getLogger(__name__)

async def connect_db(app: FastAPI):
    """
    Create a database engine and store it in the app state.
    
    This is called during application startup. Raises exceptions (not HTTPException)
    so FastAPI can properly handle startup failures.
    """
    try:
        app.state.db_engine = create_engine(settings.railway_db_url)
        logger.info("Database engine created successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        # Raise the exception directly (not HTTPException) so FastAPI can handle startup failures properly
        raise

async def close_db(app: FastAPI):
    """
    Close the database engine during application shutdown.
    """
    if hasattr(app.state, 'db_engine') and app.state.db_engine:
        await app.state.db_engine.dispose()