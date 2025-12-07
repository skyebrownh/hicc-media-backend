from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from app.dependencies import verify_api_key
from app.routers import *
from app.db.db import connect_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db(app)
    yield
    await close_db(app)

app = FastAPI(lifespan=lifespan)
    
@app.get("/", dependencies=[Depends(verify_api_key)])
async def root():
    return {"message": "Hello World!"}

app.include_router(user_router, dependencies=[Depends(verify_api_key)])
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