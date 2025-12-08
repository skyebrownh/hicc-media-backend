from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.dependencies import verify_api_key
from app.routers import *
from app.db.database import connect_db, close_db

# Define the lifespan event to manage startup and shutdown tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database when the application starts
    await connect_db(app)
    # Yield control to the application
    yield
    # Close the database connection when the application shuts down
    await close_db(app)

# Create the FastAPI application with the defined lifespan and global dependencies
app = FastAPI(lifespan=lifespan, dependencies=[Depends(verify_api_key)])

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