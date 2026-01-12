from uuid import UUID
from typing import AsyncGenerator, Annotated
from sqlmodel import Session
from fastapi import Request, HTTPException, status, Depends

from app.settings import settings
from app.db.models import Role
from app.utils.helpers import raise_exception_if_not_found

def verify_api_key(request: Request) -> None:
    """
    Dependency to verify API key from request headers.
    
    Checks for 'x-api-key' header and validates it against the configured
    API key. Raises HTTPException if the key is missing or invalid.
    """
    api_key = request.headers.get("x-api-key")

    if not api_key or api_key.strip() != settings.fast_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized: Invalid or missing API Key"
        )

APIKeyDep = Annotated[str, Depends(verify_api_key)]

async def get_db_session(request: Request) -> AsyncGenerator[Session, None]:
    """
    Dependency that provides a database session for each request.
    
    Each request uses its own session from the engine. The session is
    automatically closed when the request completes.
    """
    with Session(request.app.state.db_engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db_session)]

def require_role(id: UUID, session: SessionDep) -> Role:
    role = session.get(Role, id)
    raise_exception_if_not_found(role, Role)
    return role

RoleDep = Annotated[Role, Depends(require_role)]