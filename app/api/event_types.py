from fastapi import APIRouter, status, Response
from sqlmodel import select

from app.db.models import EventType, EventTypeCreate, EventTypeUpdate
from app.utils.dependencies import SessionDep, EventTypeDep
from app.services.domain import create_object, update_object

router = APIRouter(prefix="/event_types")

@router.get("", response_model=list[EventType])
def get_all_event_types(session: SessionDep):
    return session.exec(select(EventType)).all()

@router.get("/{id}", response_model=EventType)
def get_single_event_type(event_type: EventTypeDep):
    return event_type

@router.post("", response_model=EventType, status_code=status.HTTP_201_CREATED)
def post_event_type(payload: EventTypeCreate, session: SessionDep):
    return create_object(session, payload, EventType)

@router.patch("/{id}", response_model=EventType)
def patch_event_type(payload: EventTypeUpdate, session: SessionDep, event_type: EventTypeDep):
    return update_object(session, payload, event_type)

@router.delete("/{id}")
def delete_event_type(session: SessionDep, event_type: EventTypeDep):
    session.delete(event_type)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)