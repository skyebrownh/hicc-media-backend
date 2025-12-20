import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import create_engine, SQLModel
from app.settings import settings
from app.db.models import Role, ProficiencyLevel, EventType, Team, User, TeamUser, UserRole, Schedule, Event, EventAssignment, UserUnavailablePeriod

engine = create_engine(settings.railway_database_url)

def drop_and_recreate_schema():
    # Close any existing connections
    engine.dispose()

    # Use a connection for DDL operations
    with engine.connect() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE")
        conn.exec_driver_sql("CREATE SCHEMA public")
        conn.commit()

    # Create all tables using the engine directly
    SQLModel.metadata.create_all(engine)
    print("Schema dropped and recreated successfully")

if __name__ == "__main__":
    drop_and_recreate_schema()