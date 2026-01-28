import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import csv
from datetime import datetime
from sqlmodel import create_engine, Session

from app.db.scripts.seed import truncate_all, create_roles, create_proficiency_levels, create_event_types, create_teams, create_users, create_team_users, create_user_roles, create_events, create_event_assignments
from app.db.models import Schedule, User, UserUnavailablePeriod

engine = create_engine(os.getenv("DATABASE_URL"))

def create_sample_schedules():
    return [
        Schedule(month=10, year=2025),
        Schedule(month=11, year=2025),
        Schedule(month=12, year=2025),
        Schedule(month=1, year=2026)
    ]

def create_sample_user_unavailable_periods(users: list[User]):
    user_unavailable_periods = []
    with open(project_root / 'app/db/csv/user_unavailable_periods.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header row
        for row in reader:
            user_first_name, starts_at_csv, ends_at_csv = row
            user = next((user for user in users if user.first_name == user_first_name), None)
            include_row = starts_at_csv.startswith("2025-10") or starts_at_csv.startswith("2025-11") or starts_at_csv.startswith("2025-12")
            if user and include_row:
                user_unavailable_periods.append(UserUnavailablePeriod(
                    user_id=user.id,
                    starts_at=datetime.strptime(starts_at_csv, '%Y-%m-%d').date(),
                    ends_at=datetime.strptime(ends_at_csv, '%Y-%m-%d').date(),
                ))
    return user_unavailable_periods

def seed_sample_data():
    print("Seeding sample data...")
    with Session(engine) as session:
        roles = create_roles()
        proficiency_levels = create_proficiency_levels()
        event_types = create_event_types()
        teams = create_teams()
        users = create_users()
        schedules = create_sample_schedules()

        # Add and flush referenced objects first so they exist in the database
        session.add_all(roles)
        session.add_all(proficiency_levels)
        session.add_all(event_types)
        session.add_all(teams)
        session.add_all(users)
        session.add_all(schedules)
        session.flush()

        # Now create objects that reference the previously added objects
        team_users = create_team_users(teams, users)
        user_roles = create_user_roles(users, roles, proficiency_levels)
        events = create_events(schedules, event_types, teams)
        event_assignments = create_event_assignments(events, roles, users, event_types)
        user_unavailable_periods = create_sample_user_unavailable_periods(users)

        # Add child objects
        session.add_all(team_users)
        session.add_all(user_roles)
        session.add_all(events)
        session.add_all(event_assignments)
        session.add_all(user_unavailable_periods)

        # Commit the transaction
        session.commit()
        print("Sample data seeded successfully")

if __name__ == "__main__":
    truncate_all()
    seed_sample_data()