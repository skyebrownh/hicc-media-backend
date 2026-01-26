import logging
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import text
from contextlib import asynccontextmanager

from app.settings import settings
from app.utils.dependencies import verify_api_key, get_db_session, SessionDep
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

# Define the lifespan event to manage startup and shutdown tasks, such as database connections
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db(app)
    yield
    await close_db(app)

# Create the FastAPI application with the defined lifespan, global dependencies, and metadata
tags_metadata = [
    {
        "name": "health",
        "description": "Health check endpoint that verifies application and database connectivity",
    },
    {
        "name": "roles",
        "description": "Role are the skills/positions that can be assigned to users and identify slots for event assignments",
    },
    {
        "name": "proficiency_levels",
        "description": "Proficiency levels are the levels of expertise for a role",
    },
    {
        "name": "event_types",
        "description": "Event types are the types of events that can be created",
    },
    {
        "name": "teams",
        "description": "Teams are groups of users that work together on events",
    },
    {
        "name": "users",
        "description": "Users are the people who work on events",
    },
    {
        "name": "team_users",
        "description": "Team users are the users who are part of a team",
    },
    {
        "name": "user_roles",
        "description": "User roles are the roles that a user has",
    },
    {
        "name": "schedules",
        "description": "Schedules are the time periods that events can be assigned to (month-long)",
    },
    {
        "name": "events",
        "description": "Events are the individual occurrences within a schedule",
    },
    {
        "name": "event_assignments",
        "description": "Event assignments are the assignments of a user to a role for an event",
    },
    {
        "name": "user_unavailable_periods",
        "description": "User unavailable periods are the time periods that a user is unavailable",
    },
]

app = FastAPI(
    title="StewardHQ API",
    description="API powering StewardHQ's scheduling, availability, and team management platform",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan, 
    dependencies=[Depends(verify_api_key), Depends(get_db_session)]
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