import datetime
from fastapi import status, Response
from app.utils.helpers import get_date_details

def assert_empty_list_200(response: Response) -> None:
    """
    Assert that a response is an empty list and returns a 200 OK status code.
    
    Args:
        response: The response to assert
    """
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0
    assert response.json() == []

def get_date_values_query(date_str: str) -> dict:
    date_details = get_date_details(datetime.date.fromisoformat(date_str))
    date_query = f"""
        (
            '{date_str}',
            {date_details["calendar_year"]},
            {date_details["calendar_month"]},
            '{date_details["month_name"]}',
            '{date_details["month_abbr"]}',
            {date_details["calendar_day"]},
            {date_details["weekday"]},
            '{date_details["weekday_name"]}',
            {str(date_details["is_weekend"]).lower()},
            {str(date_details["is_weekday"]).lower()},
            {str(date_details["is_holiday"]).lower()},
            {date_details["week_number"]},
            {str(date_details["is_first_of_month"]).lower()},
            {str(date_details["is_last_of_month"]).lower()},
            {date_details["calendar_quarter"]},
            {date_details["weekday_of_month"]}
        )
        """
    return date_query

def insert_dates(date_strings: list[str]) -> str:
    """
    Generate an INSERT query string for one or more dates into the dates table.
    
    Args:
        date_strings: List of date strings in 'YYYY-MM-DD' format
    
    Returns:
        SQL query string to insert the dates
    """
    if not date_strings:
        return ""
    
    date_values = ", ".join(get_date_values_query(date_str) for date_str in date_strings)
    
    query = f"""
        INSERT INTO dates (
            date, calendar_year, calendar_month, month_name, month_abbr, calendar_day, weekday, 
            weekday_name, is_weekend, is_weekday, is_holiday, week_number, is_first_of_month, 
            is_last_of_month, calendar_quarter, weekday_of_month
        )
        VALUES {date_values};
    """
    
    return query

def insert_media_roles(media_roles: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more media roles into the media_roles table.
    
    Args:
        media_roles: List of dictionaries, each representing a media role. Each dict can contain:
            - media_role_id (optional, str/uuid): UUID string for the media role. If provided for any role,
              must be provided for all roles in the same INSERT.
            - media_role_name (required, str): Name of the media role
            - description (optional, str or None): Description of the media role. Can be None.
            - sort_order (required, int): Sort order for the media role
            - media_role_code (required, str): Unique code for the media role
            - is_active (optional, bool): Whether the media role is active (defaults to True).
              If provided for any role, must be provided for all roles in the same INSERT.
    
    Returns:
        SQL query string to insert the media roles
    """
    if not media_roles:
        return ""
    
    # Determine which optional columns to include
    # For media_role_id and is_active: only include if ALL roles have them (since they have DB defaults)
    # For description: include if ANY role has it (can be NULL for others)
    has_media_role_id = all("media_role_id" in role for role in media_roles)
    has_description = any("description" in role for role in media_roles)
    has_is_active = all("is_active" in role for role in media_roles)
    
    def get_media_role_values(role: dict) -> str:
        """Generate VALUES clause for a single media role"""
        values = []
        
        # Handle media_role_id (optional, only if all roles have it)
        if has_media_role_id:
            values.append(f"'{role['media_role_id']}'")
        
        # Required fields
        name = str(role["media_role_name"]).replace("'", "''")
        values.append(f"'{name}'")
        
        # Handle description (optional, can be None)
        if has_description:
            if "description" in role:
                if role["description"] is None:
                    values.append("NULL")
                else:
                    # Escape single quotes in description
                    desc = str(role["description"]).replace("'", "''")
                    values.append(f"'{desc}'")
            else:
                values.append("NULL")
        
        # Required fields
        values.append(str(role["sort_order"]))
        
        # Handle is_active (optional, only if all roles have it)
        if has_is_active:
            values.append(str(role["is_active"]).lower())
        
        # Required field
        code = str(role["media_role_code"]).replace("'", "''")
        values.append(f"'{code}'")
        
        return f"({', '.join(values)})"
    
    # Build column list
    columns = []
    if has_media_role_id:
        columns.append("media_role_id")
    columns.append("media_role_name")
    if has_description:
        columns.append("description")
    columns.append("sort_order")
    if has_is_active:
        columns.append("is_active")
    columns.append("media_role_code")
    
    # Generate VALUES clauses for all roles
    role_values = ", ".join(get_media_role_values(role) for role in media_roles)
    
    query = f"""
        INSERT INTO media_roles ({', '.join(columns)})
        VALUES {role_values};
    """
    
    return query

def insert_teams(teams: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more teams into the teams table.
    
    Args:
        teams: List of dictionaries, each representing a team. Each dict can contain:
            - team_id (optional, str/uuid): UUID string for the team. If provided for any team,
              must be provided for all teams in the same INSERT.
            - team_name (required, str): Name of the team
            - team_code (required, str): Unique code for the team
            - is_active (optional, bool): Whether the team is active (defaults to True).
              If provided for any team, must be provided for all teams in the same INSERT.
    
    Returns:
        SQL query string to insert the teams
    """
    if not teams:
        return ""
    
    has_team_id = all("team_id" in team for team in teams)
    has_is_active = all("is_active" in team for team in teams)
    
    def get_team_values(team: dict) -> str:
        """Generate VALUES clause for a single team"""
        values = []
        
        if has_team_id:
            values.append(f"'{team['team_id']}'")
        
        name = str(team["team_name"]).replace("'", "''")
        values.append(f"'{name}'")
        
        if has_is_active:
            values.append(str(team["is_active"]).lower())
        
        code = str(team["team_code"]).replace("'", "''")
        values.append(f"'{code}'")
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_team_id:
        columns.append("team_id")
    columns.append("team_name")
    if has_is_active:
        columns.append("is_active")
    columns.append("team_code")
    
    team_values = ", ".join(get_team_values(team) for team in teams)
    
    query = f"""
        INSERT INTO teams ({', '.join(columns)})
        VALUES {team_values};
    """
    
    return query

def insert_users(users: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more users into the users table.
    
    Args:
        users: List of dictionaries, each representing a user. Each dict can contain:
            - user_id (optional, str/uuid): UUID string for the user. If provided for any user,
              must be provided for all users in the same INSERT.
            - first_name (required, str): First name of the user
            - last_name (required, str): Last name of the user
            - email (optional, str or None): Email address of the user. Can be None.
            - phone (required, str): Phone number of the user
            - is_active (optional, bool): Whether the user is active (defaults to True).
              If provided for any user, must be provided for all users in the same INSERT.
    
    Returns:
        SQL query string to insert the users
    """
    if not users:
        return ""
    
    has_user_id = all("user_id" in user for user in users)
    has_email = any("email" in user for user in users)
    has_is_active = all("is_active" in user for user in users)
    
    def get_user_values(user: dict) -> str:
        """Generate VALUES clause for a single user"""
        values = []
        
        if has_user_id:
            values.append(f"'{user['user_id']}'")
        
        first_name = str(user["first_name"]).replace("'", "''")
        values.append(f"'{first_name}'")
        
        last_name = str(user["last_name"]).replace("'", "''")
        values.append(f"'{last_name}'")
        
        if has_email:
            if "email" in user:
                if user["email"] is None:
                    values.append("NULL")
                else:
                    email = str(user["email"]).replace("'", "''")
                    values.append(f"'{email}'")
            else:
                values.append("NULL")
        
        phone = str(user["phone"]).replace("'", "''")
        values.append(f"'{phone}'")
        
        if has_is_active:
            values.append(str(user["is_active"]).lower())
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_user_id:
        columns.append("user_id")
    columns.append("first_name")
    columns.append("last_name")
    if has_email:
        columns.append("email")
    columns.append("phone")
    if has_is_active:
        columns.append("is_active")
    
    user_values = ", ".join(get_user_values(user) for user in users)
    
    query = f"""
        INSERT INTO users ({', '.join(columns)})
        VALUES {user_values};
    """
    
    return query

def insert_team_users(team_users: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more team_users into the team_users table.
    
    Args:
        team_users: List of dictionaries, each representing a team_user. Each dict can contain:
            - team_user_id (optional, str/uuid): UUID string for the team_user. If provided for any team_user,
              must be provided for all team_users in the same INSERT.
            - team_id (required, str/uuid): UUID string for the team
            - user_id (required, str/uuid): UUID string for the user
            - is_active (optional, bool): Whether the team_user is active (defaults to True).
              If provided for any team_user, must be provided for all team_users in the same INSERT.
    
    Returns:
        SQL query string to insert the team_users
    """
    if not team_users:
        return ""
    
    has_team_user_id = all("team_user_id" in tu for tu in team_users)
    has_is_active = all("is_active" in tu for tu in team_users)
    
    def get_team_user_values(team_user: dict) -> str:
        """Generate VALUES clause for a single team_user"""
        values = []
        
        if has_team_user_id:
            values.append(f"'{team_user['team_user_id']}'")
        
        values.append(f"'{team_user['team_id']}'")
        values.append(f"'{team_user['user_id']}'")
        
        if has_is_active:
            values.append(str(team_user["is_active"]).lower())
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_team_user_id:
        columns.append("team_user_id")
    columns.append("team_id")
    columns.append("user_id")
    if has_is_active:
        columns.append("is_active")
    
    team_user_values = ", ".join(get_team_user_values(tu) for tu in team_users)
    
    query = f"""
        INSERT INTO team_users ({', '.join(columns)})
        VALUES {team_user_values};
    """
    
    return query

def insert_proficiency_levels(proficiency_levels: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more proficiency levels into the proficiency_levels table.
    
    Args:
        proficiency_levels: List of dictionaries, each representing a proficiency level. Each dict can contain:
            - proficiency_level_id (optional, str/uuid): UUID string for the proficiency level. If provided for any level,
              must be provided for all levels in the same INSERT.
            - proficiency_level_name (required, str): Name of the proficiency level
            - proficiency_level_number (optional, int or None): Number of the proficiency level. Can be None.
            - proficiency_level_code (required, str): Unique code for the proficiency level
            - is_active (optional, bool): Whether the proficiency level is active (defaults to True).
              If provided for any level, must be provided for all levels in the same INSERT.
            - is_assignable (optional, bool): Whether the proficiency level is assignable (defaults to False).
              If provided for any level, must be provided for all levels in the same INSERT.
    
    Returns:
        SQL query string to insert the proficiency levels
    """
    if not proficiency_levels:
        return ""
    
    has_proficiency_level_id = all("proficiency_level_id" in pl for pl in proficiency_levels)
    has_proficiency_level_number = any("proficiency_level_number" in pl for pl in proficiency_levels)
    has_is_active = all("is_active" in pl for pl in proficiency_levels)
    has_is_assignable = all("is_assignable" in pl for pl in proficiency_levels)
    
    def get_proficiency_level_values(pl: dict) -> str:
        """Generate VALUES clause for a single proficiency level"""
        values = []
        
        if has_proficiency_level_id:
            values.append(f"'{pl['proficiency_level_id']}'")
        
        name = str(pl["proficiency_level_name"]).replace("'", "''")
        values.append(f"'{name}'")
        
        if has_proficiency_level_number:
            if "proficiency_level_number" in pl:
                if pl["proficiency_level_number"] is None:
                    values.append("NULL")
                else:
                    values.append(str(pl["proficiency_level_number"]))
            else:
                values.append("NULL")
        
        if has_is_active:
            values.append(str(pl["is_active"]).lower())
        
        code = str(pl["proficiency_level_code"]).replace("'", "''")
        values.append(f"'{code}'")
        
        if has_is_assignable:
            values.append(str(pl["is_assignable"]).lower())
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_proficiency_level_id:
        columns.append("proficiency_level_id")
    columns.append("proficiency_level_name")
    if has_proficiency_level_number:
        columns.append("proficiency_level_number")
    if has_is_active:
        columns.append("is_active")
    columns.append("proficiency_level_code")
    if has_is_assignable:
        columns.append("is_assignable")
    
    pl_values = ", ".join(get_proficiency_level_values(pl) for pl in proficiency_levels)
    
    query = f"""
        INSERT INTO proficiency_levels ({', '.join(columns)})
        VALUES {pl_values};
    """
    
    return query

def insert_user_roles(user_roles: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more user_roles into the user_roles table.
    
    Args:
        user_roles: List of dictionaries, each representing a user_role. Each dict can contain:
            - user_role_id (optional, str/uuid): UUID string for the user_role. If provided for any user_role,
              must be provided for all user_roles in the same INSERT.
            - user_id (required, str/uuid): UUID string for the user
            - media_role_id (required, str/uuid): UUID string for the media role
            - proficiency_level_id (required, str/uuid): UUID string for the proficiency level
    
    Returns:
        SQL query string to insert the user_roles
    """
    if not user_roles:
        return ""
    
    has_user_role_id = all("user_role_id" in ur for ur in user_roles)
    
    def get_user_role_values(user_role: dict) -> str:
        """Generate VALUES clause for a single user_role"""
        values = []
        
        if has_user_role_id:
            values.append(f"'{user_role['user_role_id']}'")
        
        values.append(f"'{user_role['user_id']}'")
        values.append(f"'{user_role['media_role_id']}'")
        values.append(f"'{user_role['proficiency_level_id']}'")
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_user_role_id:
        columns.append("user_role_id")
    columns.append("user_id")
    columns.append("media_role_id")
    columns.append("proficiency_level_id")
    
    ur_values = ", ".join(get_user_role_values(ur) for ur in user_roles)
    
    query = f"""
        INSERT INTO user_roles ({', '.join(columns)})
        VALUES {ur_values};
    """
    
    return query

def insert_schedule_date_types(schedule_date_types: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more schedule_date_types into the schedule_date_types table.
    
    Args:
        schedule_date_types: List of dictionaries, each representing a schedule_date_type. Each dict can contain:
            - schedule_date_type_id (optional, str/uuid): UUID string for the schedule_date_type. If provided for any type,
              must be provided for all types in the same INSERT.
            - schedule_date_type_name (required, str): Name of the schedule_date_type
            - schedule_date_type_code (required, str): Unique code for the schedule_date_type
            - is_active (optional, bool): Whether the schedule_date_type is active (defaults to True).
              If provided for any type, must be provided for all types in the same INSERT.
    
    Returns:
        SQL query string to insert the schedule_date_types
    """
    if not schedule_date_types:
        return ""
    
    has_schedule_date_type_id = all("schedule_date_type_id" in sdt for sdt in schedule_date_types)
    has_is_active = all("is_active" in sdt for sdt in schedule_date_types)
    
    def get_schedule_date_type_values(sdt: dict) -> str:
        """Generate VALUES clause for a single schedule_date_type"""
        values = []
        
        if has_schedule_date_type_id:
            values.append(f"'{sdt['schedule_date_type_id']}'")
        
        name = str(sdt["schedule_date_type_name"]).replace("'", "''")
        values.append(f"'{name}'")
        
        if has_is_active:
            values.append(str(sdt["is_active"]).lower())
        
        code = str(sdt["schedule_date_type_code"]).replace("'", "''")
        values.append(f"'{code}'")
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_schedule_date_type_id:
        columns.append("schedule_date_type_id")
    columns.append("schedule_date_type_name")
    if has_is_active:
        columns.append("is_active")
    columns.append("schedule_date_type_code")
    
    sdt_values = ", ".join(get_schedule_date_type_values(sdt) for sdt in schedule_date_types)
    
    query = f"""
        INSERT INTO schedule_date_types ({', '.join(columns)})
        VALUES {sdt_values};
    """
    
    return query

def insert_schedules(schedules: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more schedules into the schedules table.
    
    Args:
        schedules: List of dictionaries, each representing a schedule. Each dict can contain:
            - schedule_id (optional, str/uuid): UUID string for the schedule. If provided for any schedule,
              must be provided for all schedules in the same INSERT.
            - month_start_date (required, str): Date string in 'YYYY-MM-DD' format
            - notes (optional, str or None): Notes for the schedule. Can be None.
            - is_active (optional, bool): Whether the schedule is active (defaults to True).
              If provided for any schedule, must be provided for all schedules in the same INSERT.
    
    Returns:
        SQL query string to insert the schedules
    """
    if not schedules:
        return ""
    
    has_schedule_id = all("schedule_id" in s for s in schedules)
    has_notes = any("notes" in s for s in schedules)
    has_is_active = all("is_active" in s for s in schedules)
    
    def get_schedule_values(schedule: dict) -> str:
        """Generate VALUES clause for a single schedule"""
        values = []
        
        if has_schedule_id:
            values.append(f"'{schedule['schedule_id']}'")
        
        values.append(f"'{schedule['month_start_date']}'")
        
        if has_notes:
            if "notes" in schedule:
                if schedule["notes"] is None:
                    values.append("NULL")
                else:
                    notes = str(schedule["notes"]).replace("'", "''")
                    values.append(f"'{notes}'")
            else:
                values.append("NULL")
        
        if has_is_active:
            values.append(str(schedule["is_active"]).lower())
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_schedule_id:
        columns.append("schedule_id")
    columns.append("month_start_date")
    if has_notes:
        columns.append("notes")
    if has_is_active:
        columns.append("is_active")
    
    schedule_values = ", ".join(get_schedule_values(s) for s in schedules)
    
    query = f"""
        INSERT INTO schedules ({', '.join(columns)})
        VALUES {schedule_values};
    """
    
    return query

def insert_schedule_dates(schedule_dates: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more schedule_dates into the schedule_dates table.
    
    Args:
        schedule_dates: List of dictionaries, each representing a schedule_date. Each dict can contain:
            - schedule_date_id (optional, str/uuid): UUID string for the schedule_date. If provided for any schedule_date,
              must be provided for all schedule_dates in the same INSERT.
            - schedule_id (required, str/uuid): UUID string for the schedule
            - date (required, str): Date string in 'YYYY-MM-DD' format
            - team_id (optional, str/uuid or None): UUID string for the team. Can be None.
            - schedule_date_type_id (required, str/uuid): UUID string for the schedule_date_type
            - notes (optional, str or None): Notes for the schedule_date. Can be None.
            - is_active (optional, bool): Whether the schedule_date is active (defaults to True).
              If provided for any schedule_date, must be provided for all schedule_dates in the same INSERT.
    
    Returns:
        SQL query string to insert the schedule_dates
    """
    if not schedule_dates:
        return ""
    
    has_schedule_date_id = all("schedule_date_id" in sd for sd in schedule_dates)
    has_team_id = any("team_id" in sd for sd in schedule_dates)
    has_notes = any("notes" in sd for sd in schedule_dates)
    has_is_active = all("is_active" in sd for sd in schedule_dates)
    
    def get_schedule_date_values(sd: dict) -> str:
        """Generate VALUES clause for a single schedule_date"""
        values = []
        
        if has_schedule_date_id:
            values.append(f"'{sd['schedule_date_id']}'")
        
        values.append(f"'{sd['schedule_id']}'")
        values.append(f"'{sd['date']}'")
        
        if has_team_id:
            if "team_id" in sd:
                if sd["team_id"] is None:
                    values.append("NULL")
                else:
                    values.append(f"'{sd['team_id']}'")
            else:
                values.append("NULL")
        
        values.append(f"'{sd['schedule_date_type_id']}'")
        
        if has_notes:
            if "notes" in sd:
                if sd["notes"] is None:
                    values.append("NULL")
                else:
                    notes = str(sd["notes"]).replace("'", "''")
                    values.append(f"'{notes}'")
            else:
                values.append("NULL")
        
        if has_is_active:
            values.append(str(sd["is_active"]).lower())
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_schedule_date_id:
        columns.append("schedule_date_id")
    columns.append("schedule_id")
    columns.append("date")
    if has_team_id:
        columns.append("team_id")
    columns.append("schedule_date_type_id")
    if has_notes:
        columns.append("notes")
    if has_is_active:
        columns.append("is_active")
    
    sd_values = ", ".join(get_schedule_date_values(sd) for sd in schedule_dates)
    
    query = f"""
        INSERT INTO schedule_dates ({', '.join(columns)})
        VALUES {sd_values};
    """
    
    return query

def insert_schedule_date_roles(schedule_date_roles: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more schedule_date_roles into the schedule_date_roles table.
    
    Args:
        schedule_date_roles: List of dictionaries, each representing a schedule_date_role. Each dict can contain:
            - schedule_date_role_id (optional, str/uuid): UUID string for the schedule_date_role. If provided for any role,
              must be provided for all roles in the same INSERT.
            - schedule_date_id (required, str/uuid): UUID string for the schedule_date
            - media_role_id (required, str/uuid): UUID string for the media role
            - is_required (optional, bool): Whether the role is required (defaults to True).
              If provided for any role, must be provided for all roles in the same INSERT.
            - is_preferred (optional, bool): Whether the role is preferred (defaults to False).
              If provided for any role, must be provided for all roles in the same INSERT.
            - assigned_user_id (optional, str/uuid or None): UUID string for the assigned user. Can be None.
            - is_active (optional, bool): Whether the schedule_date_role is active (defaults to True).
              If provided for any role, must be provided for all roles in the same INSERT.
    
    Returns:
        SQL query string to insert the schedule_date_roles
    """
    if not schedule_date_roles:
        return ""
    
    has_schedule_date_role_id = all("schedule_date_role_id" in sdr for sdr in schedule_date_roles)
    has_is_required = all("is_required" in sdr for sdr in schedule_date_roles)
    has_is_preferred = all("is_preferred" in sdr for sdr in schedule_date_roles)
    has_assigned_user_id = any("assigned_user_id" in sdr for sdr in schedule_date_roles)
    has_is_active = all("is_active" in sdr for sdr in schedule_date_roles)
    
    def get_schedule_date_role_values(sdr: dict) -> str:
        """Generate VALUES clause for a single schedule_date_role"""
        values = []
        
        if has_schedule_date_role_id:
            values.append(f"'{sdr['schedule_date_role_id']}'")
        
        values.append(f"'{sdr['schedule_date_id']}'")
        values.append(f"'{sdr['media_role_id']}'")
        
        if has_is_required:
            values.append(str(sdr["is_required"]).lower())
        
        if has_is_preferred:
            values.append(str(sdr["is_preferred"]).lower())
        
        if has_assigned_user_id:
            if "assigned_user_id" in sdr:
                if sdr["assigned_user_id"] is None:
                    values.append("NULL")
                else:
                    values.append(f"'{sdr['assigned_user_id']}'")
            else:
                values.append("NULL")
        
        if has_is_active:
            values.append(str(sdr["is_active"]).lower())
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_schedule_date_role_id:
        columns.append("schedule_date_role_id")
    columns.append("schedule_date_id")
    columns.append("media_role_id")
    if has_is_required:
        columns.append("is_required")
    if has_is_preferred:
        columns.append("is_preferred")
    if has_assigned_user_id:
        columns.append("assigned_user_id")
    if has_is_active:
        columns.append("is_active")
    
    sdr_values = ", ".join(get_schedule_date_role_values(sdr) for sdr in schedule_date_roles)
    
    query = f"""
        INSERT INTO schedule_date_roles ({', '.join(columns)})
        VALUES {sdr_values};
    """
    
    return query

def insert_user_dates(user_dates: list[dict]) -> str:
    """
    Generate an INSERT query string for one or more user_dates into the user_dates table.
    
    Args:
        user_dates: List of dictionaries, each representing a user_date. Each dict can contain:
            - user_date_id (optional, str/uuid): UUID string for the user_date. If provided for any user_date,
              must be provided for all user_dates in the same INSERT.
            - user_id (required, str/uuid): UUID string for the user
            - date (required, str): Date string in 'YYYY-MM-DD' format
    
    Returns:
        SQL query string to insert the user_dates
    """
    if not user_dates:
        return ""
    
    has_user_date_id = all("user_date_id" in ud for ud in user_dates)
    
    def get_user_date_values(user_date: dict) -> str:
        """Generate VALUES clause for a single user_date"""
        values = []
        
        if has_user_date_id:
            values.append(f"'{user_date['user_date_id']}'")
        
        values.append(f"'{user_date['user_id']}'")
        values.append(f"'{user_date['date']}'")
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_user_date_id:
        columns.append("user_date_id")
    columns.append("user_id")
    columns.append("date")
    
    ud_values = ", ".join(get_user_date_values(ud) for ud in user_dates)
    
    query = f"""
        INSERT INTO user_dates ({', '.join(columns)})
        VALUES {ud_values};
    """
    
    return query
    