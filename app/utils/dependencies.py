from uuid import UUID
from typing import AsyncGenerator, Annotated
from sqlmodel import Session
from fastapi import Request, HTTPException, status, Depends

from app.settings import settings
from app.db.models import Role, ProficiencyLevel, EventType, Team, User, Schedule
from app.utils.helpers import raise_exception_if_not_found
from app.services.queries import select_schedule_with_events_and_assignments

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

def require_proficiency_level(id: UUID, session: SessionDep) -> ProficiencyLevel:
    proficiency_level = session.get(ProficiencyLevel, id)
    raise_exception_if_not_found(proficiency_level, ProficiencyLevel)
    return proficiency_level

ProficiencyLevelDep = Annotated[ProficiencyLevel, Depends(require_proficiency_level)]

def require_event_type(id: UUID, session: SessionDep) -> EventType:
    event_type = session.get(EventType, id)
    raise_exception_if_not_found(event_type, EventType)
    return event_type

EventTypeDep = Annotated[EventType, Depends(require_event_type)]

def require_team(id: UUID, session: SessionDep) -> Team:
    team = session.get(Team, id)
    raise_exception_if_not_found(team, Team)
    return team

TeamDep = Annotated[Team, Depends(require_team)]

def require_user(id: UUID, session: SessionDep) -> User:
    user = session.get(User, id)
    raise_exception_if_not_found(user, User)
    return user

UserDep = Annotated[User, Depends(require_user)]

def require_schedule(id: UUID, session: SessionDep) -> Schedule:
    schedule = session.get(Schedule, id)
    raise_exception_if_not_found(schedule, Schedule)
    return schedule

ScheduleDep = Annotated[Schedule, Depends(require_schedule)]

def require_schedule_with_events_and_assignments(id: UUID, session: SessionDep) -> Schedule:
    schedule = select_schedule_with_events_and_assignments(session, id)
    raise_exception_if_not_found(schedule, Schedule)
    return schedule

ScheduleWithEventsAndAssignmentsDep = Annotated[Schedule, Depends(require_schedule_with_events_and_assignments)]