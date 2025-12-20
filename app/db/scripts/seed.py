import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import csv
import calendar
from datetime import date, time, datetime, timezone, timedelta
from sqlmodel import create_engine, Session
from app.settings import settings
from app.db.models import Role, ProficiencyLevel, EventType, Team, User, TeamUser, UserRole, Schedule, Event, EventAssignment, UserUnavailablePeriod

engine = create_engine(settings.railway_database_url)

def create_roles():
    roles = [
        {"name": "ProPresenter", "code": "propresenter", "order": 10},
        {"name": "Sound", "code": "sound", "order": 20},
        {"name": "Lighting", "code": "lighting", "order": 30},
        {"name": "Camera Director", "code": "camera_director", "order": 40},
        {"name": "Main Camera 1", "code": "main_camera_1", "order": 50},
        {"name": "Main Camera 2", "code": "main_camera_2", "order": 60},
        {"name": "Mobile Camera 3", "code": "mobile_camera_3", "order": 70},
        {"name": "Mobile Camera 4", "code": "mobile_camera_4", "order": 80},
        {"name": "On Call", "code": "on_call", "order": 90},
    ]
    return [Role(**role) for role in roles]

def create_proficiency_levels():
    proficiency_levels = [
        {"name": "Untrained", "code": "untrained", "rank": 0, "is_assignable": False},
        {"name": "In Training", "code": "in_training", "rank": 1, "is_assignable": False},
        {"name": "Knowledgeable", "code": "knowledgeable", "rank": 2, "is_assignable": False},
        {"name": "Novice", "code": "novice", "rank": 3, "is_assignable": True},
        {"name": "Proficient", "code": "proficient", "rank": 4, "is_assignable": True},
        {"name": "Expert", "code": "expert", "rank": 5, "is_assignable": True},
    ]
    return [ProficiencyLevel(**proficiency_level) for proficiency_level in proficiency_levels]

def create_event_types():
    event_types = [
        {"name": "Service", "code": "service"},
        {"name": "Special Event", "code": "special_event"},
        {"name": "Rehearsal", "code": "rehearsal"},
        {"name": "Training", "code": "training"},
        {"name": "Prayer", "code": "prayer"},
    ]
    return [EventType(**event_type) for event_type in event_types]

def create_teams():
    teams = [
        {"name": "Alpha", "code": "alpha"},
        {"name": "Omega", "code": "omega"},
    ]
    return [Team(**team) for team in teams]

def create_users():
    users = [
        {"first_name": "Johnathan", "last_name": "Vaughn", "email": None, "phone": "2026413546", "is_active": True},
        {"first_name": "Antoinette", "last_name": "Pitts", "email": None, "phone": "2702685127", "is_active": False},
        {"first_name": "Jaime", "last_name": "Boyd", "email": None, "phone": "2702722896", "is_active": True},
        {"first_name": "Michael", "last_name": "Hudson", "email": "mhud32@gmail.com", "phone": "2708728388", "is_active": True},
        {"first_name": "William", "last_name": "Gilmore", "email": None, "phone": "2705055383", "is_active": True},
        {"first_name": "Skye", "last_name": "Brown", "email": "skye.brownh@gmail.com", "phone": "2703008405", "is_active": True},
        {"first_name": "Horace", "last_name": "Dillard", "email": None, "phone": "2703196555", "is_active": True},
        {"first_name": "Andrew", "last_name": "Roach", "email": None, "phone": "5126399960", "is_active": False},
        {"first_name": "Gary", "last_name": "Elias Sr", "email": None, "phone": "2703175566", "is_active": True},
        {"first_name": "Vivian", "last_name": "Robinson", "email": None, "phone": "9312188779", "is_active": True},
        {"first_name": "Frank", "last_name": "Anderson", "email": None, "phone": "2702689679", "is_active": True},
        {"first_name": "Marcus", "last_name": "Pitts", "email": "marcuspitts25@gmail.com", "phone": "2705067988", "is_active": True},
        {"first_name": "Mario", "last_name": "Hodge", "email": None, "phone": "2703006425", "is_active": True},
        {"first_name": "Alexis", "last_name": "Williams", "email": None, "phone": "5023782871", "is_active": True},
        {"first_name": "Harry", "last_name": "Parent", "email": None, "phone": "2703178092", "is_active": True},
        {"first_name": "Jarrell", "last_name": "Russell", "email": None, "phone": "2703199324", "is_active": True},
    ]
    return [User(**user) for user in users]

def create_team_users(teams: list[Team], users: list[User]):
    team_users = []
    for team in teams:
        for user in users:
            if team.name == "Alpha" and user.first_name in ["Michael", "William", "Gary", "Skye", "Vivian", "Horace", "Alexis", "Harry"]:
                team_users.append(TeamUser(team_id=team.id, user_id=user.id, is_active=True))
            elif team.name == "Omega" and user.first_name in ["Marcus", "Mario", "Jaime", "Frank", "Johnathan", "Andrew", "Jarrell"]:
                team_users.append(TeamUser(team_id=team.id, user_id=user.id, is_active=True))
    return team_users

def create_user_roles(users: list[User], roles: list[Role], proficiency_levels: list[ProficiencyLevel]):
    user_roles = []
    # Load CSV data
    with open(project_root / 'app/db/csv/user_roles.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header row
        for row in reader:
            user_first_name, role_code, pl_rank = row
            # Find the user, role, and proficiency level
            user = next((user for user in users if user.first_name == user_first_name), None)
            role = next((role for role in roles if role.code == role_code), None)
            pl = next((pl for pl in proficiency_levels if pl.rank == int(pl_rank)), None)
            # If the user, role, and proficiency level are found, add the user role to the list
            if user and role and pl:
                user_roles.append(UserRole(user_id=user.id, role_id=role.id, proficiency_level_id=pl.id, is_active=True))
    return user_roles

def create_schedules():
    schedules = []
    for month in range(1, 13):
        for year in range(2025, 2027):
            schedules.append(Schedule(month=month, year=year))
    return schedules

def create_events(schedules: list[Schedule], event_types: list[EventType], teams: list[Team]):
    # helper constants and functions
    WEEKDAY_MAP = {
        calendar.SUNDAY: {
            "type": "service",
            "start": time(9, 0),
            "end": time(12, 30),
        },
        calendar.WEDNESDAY: {
            "type": "service",
            "start": time(18, 30),
            "end": time(20, 30),
        },
        calendar.SATURDAY: {
            "type": "prayer",
            "start": time(10, 0),
            "end": time(11, 0),
        },
    }

    def get_weekday_number_of_month(date_obj: date) -> int:
        """
        Calculates the 'nth' occurence of a specific weekday within its month.
        """
        weekday_number = 1 + (date_obj.day - 1) // 7
        return weekday_number
    
    def get_weekday_dates(year: int, month: int, weekdays: set[int]):
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            for wd in weekdays:
                day = week[wd]
                if day != 0:
                    yield date(year, month, day)

    def generate_events_for_month(year: int, month: int, weekday_map: dict[int, dict[str, str | time]]):
        for weekday, times in weekday_map.items():
            for d in get_weekday_dates(year, month, {weekday}):
                yield {
                    "date": d,
                    "starts_at": datetime.combine(d, times["start"], tzinfo=timezone.utc),
                    "ends_at": datetime.combine(d, times["end"], tzinfo=timezone.utc),
                    "weekday": weekday,
                    "event_type": times["type"],
                }

    # setup
    special_event_type = next((event_type for event_type in event_types if event_type.code == "special_event"), None)
    service_event_type = next((event_type for event_type in event_types if event_type.code == "service"), None)
    alpha_team = next((team for team in teams if team.code == "alpha"), None)
    omega_team = next((team for team in teams if team.code == "omega"), None)
    events = []

    # Insert every Sun and Wed as service where team Alpha is 1st & 3rd, and team Omega is 2nd & 4th
    # Insert every Sat as prayer
    for schedule in schedules:
        for event in generate_events_for_month(schedule.year, schedule.month, WEEKDAY_MAP):
            weekday_number = get_weekday_number_of_month(event["date"])
            team = alpha_team if weekday_number in [1,3] else omega_team if weekday_number in [2,4] else None
            event_type = next((event_type for event_type in event_types if event_type.code == event["event_type"]), None)
            events.append(Event(
                schedule_id=schedule.id,
                starts_at=event["starts_at"],
                ends_at=event["ends_at"],
                team_id=team.id if event["weekday"] != calendar.SATURDAY and team else None,
                event_type_id=event_type.id,
                title=f" {event['event_type'].title()} - {event['date'].strftime('%a %Y-%m-%d')}",
            ))

    # Update notes for existing rows based on CSV data
    with open(project_root / 'app/db/csv/events_update_notes.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header row
        for row in reader:
            date_csv, notes = row
            event_date = datetime.strptime(date_csv, '%Y-%m-%d').date()
            event = next((event for event in events if event.starts_at.date() == event_date), None)
            if event:
                event.notes = notes
                
    # Insert special events based on CSV data
    with open(project_root / 'app/db/csv/events_special.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header row
        for row in reader:
            date_csv, start_time_csv, end_time_csv, team_csv, notes = row

            event_date = datetime.strptime(date_csv, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_csv, '%H:%M').time()
            end_time = datetime.strptime(end_time_csv, '%H:%M').time()
            schedule = next((schedule for schedule in schedules if schedule.year == event_date.year and schedule.month == event_date.month), None)
            team = next((team for team in teams if team.code == team_csv), None)
            title = f"{special_event_type.name.title()} - {event_date.strftime('%a %Y-%m-%d')}"
            starts_at = datetime.combine(event_date, start_time, tzinfo=timezone.utc)
            ends_at = datetime.combine(event_date, end_time, tzinfo=timezone.utc)

            events.append(Event(
                schedule_id=schedule.id,
                starts_at=starts_at,
                ends_at=ends_at,
                team_id=team.id if team else None,
                event_type_id=special_event_type.id,
                title=title,
                notes=notes,
            ))

    # Update exception Tuesday night midweek service for Thanksgiving week as service, not special event
    update_event = next((event for event in events if event.starts_at.date() == date(2025, 11, 25)), None)
    if update_event:
        update_event.event_type_id = service_event_type.id
        update_event.title = f"{service_event_type.name.title()} - {update_event.starts_at.date().strftime('%a %Y-%m-%d')}"
        deactivate_event = next((event for event in events if event.starts_at.date() == date(2025, 11, 26)), None)
        if deactivate_event:
            deactivate_event.is_active = False

    return events

def create_event_assignments(events: list[Event], roles: list[Role], users: list[User], event_types: list[EventType]):
    event_assignments = []
    with open(project_root / 'app/db/csv/event_assignments.csv', 'r', newline='') as file:
        stripped_file = (line for line in file if line.strip())
        reader = csv.reader(stripped_file)
        next(reader)  # Skip header row
        for row in reader:
            if any(row):
                date_csv, role_code, user_first_name, event_type_code, sound_only, sound_and_pp, is_applicable, requirement_level = row

                event_type = next((event_type for event_type in event_types if event_type.code == event_type_code), None)
                event = next((event for event in events if event.starts_at.date() == datetime.strptime(date_csv, '%Y-%m-%d').date() and event.event_type_id == event_type.id), None)
                role = next((role for role in roles if role.code == role_code), None)
                user = next((user for user in users if user.first_name == user_first_name), None)
                is_applicable = is_applicable == "TRUE"

                if event and role:
                    event_assignments.append(EventAssignment(
                        event_id=event.id,
                        role_id=role.id,
                        is_applicable=is_applicable,
                        requirement_level=requirement_level,
                        assigned_user_id=user.id if user else None,
                    ))
    return event_assignments

def create_user_unavailable_periods(users: list[User]):
    user_unavailable_periods = []
    with open(project_root / 'app/db/csv/user_unavailable_periods.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header row
        for row in reader:
            user_first_name, date_csv = row
            user = next((user for user in users if user.first_name == user_first_name), None)
            if user:
                user_unavailable_periods.append(UserUnavailablePeriod(
                    user_id=user.id,
                    starts_at=datetime.strptime(date_csv, '%Y-%m-%d').date(),
                    ends_at=datetime.strptime(date_csv, '%Y-%m-%d').date() + timedelta(days=1), # ends_at is exclusive
                ))
    return user_unavailable_periods

def seed_data():
    with Session(engine) as session:
        roles = create_roles()
        proficiency_levels = create_proficiency_levels()
        event_types = create_event_types()
        teams = create_teams()
        users = create_users()
        schedules = create_schedules()

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
        user_unavailable_periods = create_user_unavailable_periods(users)

        # Add child objects
        session.add_all(team_users)
        session.add_all(user_roles)
        session.add_all(events)
        session.add_all(event_assignments)
        session.add_all(user_unavailable_periods)

        # Commit the transaction
        session.commit()
        print("Data seeded successfully")

if __name__ == "__main__":
    seed_data()
