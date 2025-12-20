from sqlmodel import create_engine, Session, SQLModel, text
from app.settings import settings
from app.db.models import Role, ProficiencyLevel, EventType, Team, User, TeamUser, UserRole, Schedule, Event, EventAssignment, UserUnavailablePeriod

engine = create_engine(settings.railway_database_url)

def drop_schema_and_create_all_tables():
    with Session(engine) as session:
        session.exec(text("DROP SCHEMA IF EXISTS public CASCADE"))
        session.exec(SQLModel.metadata.drop_all(engine))
        session.exec(SQLModel.metadata.create_all(engine))

if __name__ == "__main__":
    drop_schema_and_create_all_tables()