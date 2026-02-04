import logging
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import text
from contextlib import asynccontextmanager

from app.settings import settings
from app.utils.helpers import TAGS_METADATA
from app.utils.dependencies import verify_api_key, get_db_session, get_optional_bearer_token, SessionDep
from app.utils.logging_config import setup_logging
from app.utils.exception_handlers import register_exception_handlers
from app.db.database import connect_db, close_db
from app.api import (
    roles_router, proficiency_levels_router, event_types_router,
    users_router, teams_router, team_users_router, user_roles_router,
    schedules_router, events_router, event_assignments_router, user_unavailable_periods_router,
)

# Set up logging configuration
setup_logging()
logger = logging.getLogger(__name__)

def log_settings():
    if settings.env != "production":
        logger.warning("Running in NON-PRODUCTION mode: %s", settings.env)
    else:
        logger.info("Running in PRODUCTION mode")

    logger.info(f"Settings: {settings.model_dump_json(indent=4)}")

# Define the lifespan event to manage startup and shutdown tasks, such as database connections
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db(app)
    log_settings()
    yield
    await close_db(app)

# Create the FastAPI application with the defined lifespan, global dependencies, and metadata
app = FastAPI(
    title="StewardHQ API",
    description="API powering StewardHQ's scheduling, availability, and team management platform",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan, 
    dependencies=[Depends(verify_api_key), Depends(get_optional_bearer_token), Depends(get_db_session)],
    swagger_ui_parameters={"persistAuthorization": True}
)

# Register exception handlers
register_exception_handlers(app)

# Add CORS middleware
if settings.cors_allowed_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Health check endpoint
@app.get("/health", tags=["health"])
def health(_: Request, session: SessionDep):
    """
    Health check endpoint that verifies application and database connectivity.
        
    Status codes:
        200: Application and database are healthy
        503: Database is unavailable
    """
    # Check database connectivity
    DB_UNAVAILABLE_RESPONSE = JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "unhealthy", "database": "unavailable"})
    DB_OK_RESPONSE = JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "database": "ok"})
    try:
        # Simple query to verify connection
        result = session.exec(text("SELECT 1"))
        if result.first() is None:
            return DB_UNAVAILABLE_RESPONSE
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return DB_UNAVAILABLE_RESPONSE
    
    return DB_OK_RESPONSE

# Include routers for different resources
app.include_router(roles_router)
app.include_router(proficiency_levels_router)
app.include_router(event_types_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(team_users_router)
app.include_router(user_roles_router)
app.include_router(schedules_router)
app.include_router(events_router)
app.include_router(event_assignments_router)
app.include_router(user_unavailable_periods_router)