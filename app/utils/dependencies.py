from typing import AsyncGenerator
from sqlmodel import Session
from fastapi import Request, HTTPException, status
from app.settings import settings


def verify_api_key(request: Request):
    """
    Dependency to verify API key from request headers.
    
    Checks for 'x-api-key' header and validates it against the configured
    API key. Raises HTTPException if the key is missing or invalid.
    
    Args:
        request: FastAPI Request object
        
    Raises:
        HTTPException(401): If API key is missing or invalid
    """
    api_key = request.headers.get("x-api-key")

    if not api_key or api_key.strip() != settings.fast_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized: Invalid or missing API Key"
        )

async def get_db_session(request: Request) -> AsyncGenerator[Session, None]:
    """
    Dependency that provides a database session for each request.
    
    Each request uses its own session from the engine. The session is
    automatically closed when the request completes.
    
    Yields:
        A database session from the engine
    """
    with Session(request.app.state.db_engine) as session:
        yield session