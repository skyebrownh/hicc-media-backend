import logging
from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, text
from contextlib import asynccontextmanager
from app.utils.dependencies import verify_api_key, get_db_session
from app.utils.logging_config import setup_logging
from app.utils.exception_handlers import register_exception_handlers
from app.routers import (
    roles_router,
    proficiency_levels_router,
    event_types_router,
    users_router,
    teams_router,
    team_users_router,
    user_roles_router,
    schedules_router,
    # events_router,
    # event_assignments_router,
    # user_unavailable_periods_router,
)
from app.db.database import connect_db, close_db

# Set up logging configuration
setup_logging()
logger = logging.getLogger(__name__)

# Define the lifespan event to manage startup and shutdown tasks, such as database connections
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db(app)
    yield
    await close_db(app)

# Create the FastAPI application with the defined lifespan and global dependencies
app = FastAPI(lifespan=lifespan, dependencies=[Depends(verify_api_key)])

# Register exception handlers
register_exception_handlers(app)

# Health check endpoint
@app.get("/health")
async def health(request: Request, session: Session = Depends(get_db_session)):
    """
    Health check endpoint that verifies application and database connectivity.
    
    Returns:
        dict: Health status with "status" and "database" fields
        
    Status codes:
        200: Application and database are healthy
        503: Database is unavailable
    """
    # Check database connectivity
    db_status = "ok"
    try:
        # Simple query to verify connection
        result = session.exec(text("SELECT 1"))
        if result.first() is None:
            db_status = "unavailable"
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "database": db_status
                }
            )
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unavailable"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": db_status
            }
        )
    
    return {
        "status": "ok",
        "database": db_status
    }

# Include routers for different resources
app.include_router(roles_router)
app.include_router(proficiency_levels_router)
app.include_router(event_types_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(team_users_router)
app.include_router(user_roles_router)
app.include_router(schedules_router)
# app.include_router(events_router)
# app.include_router(event_assignments_router)
# app.include_router(user_unavailable_periods_router)