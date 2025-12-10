from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.utils.dependencies import verify_api_key
from app.utils.logging_config import setup_logging
from app.utils.exception_handlers import register_exception_handlers
from app.routers import *
from app.db.database import connect_db, close_db

# Set up logging configuration
setup_logging()

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
async def health():
    return {"status": "ok"}

# Include routers for different resources
app.include_router(user_router)
app.include_router(team_router)
app.include_router(media_role_router)
app.include_router(proficiency_level_router)
app.include_router(schedule_date_type_router)
app.include_router(date_router)
app.include_router(schedule_router)
app.include_router(user_availability_router)
app.include_router(team_user_router)
app.include_router(user_role_router)
app.include_router(schedule_date_router)
app.include_router(schedule_date_role_router)