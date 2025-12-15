import datetime
from fastapi import status, Response
from app.utils.helpers import get_date_details

def _escape_sql_string(value: str) -> str:
    """Escape single quotes in SQL string values"""
    return str(value).replace("'", "''")

def _format_sql_value(value, field_type: str = "string") -> str:
    """
    Format a Python value for SQL insertion.
    
    Args:
        value: The value to format (can be None for nullable fields)
        field_type: Type of field - "string", "uuid", "bool", "int", "date", or "nullable_string"
    
    Returns:
        Formatted SQL value string
    """
    if value is None:
        return "NULL"
    
    if field_type == "bool":
        return str(value).lower()
    elif field_type == "int":
        return str(value)
    elif field_type in ("string", "uuid", "date"):
        escaped = _escape_sql_string(value)
        return f"'{escaped}'"
    elif field_type == "nullable_string":
        # This handles the case where the field might be None (already checked above)
        escaped = _escape_sql_string(value)
        return f"'{escaped}'"
    else:
        # Default to string handling
        escaped = _escape_sql_string(str(value))
        return f"'{escaped}'"

def _has_field_all(items: list[dict], field: str) -> bool:
    """Check if all items have the specified field (all-or-none pattern for IDs/booleans)."""
    return all(field in item for item in items)

def _has_field_any(items: list[dict], field: str) -> bool:
    """Check if any item has the specified field (any-for nullable text pattern)."""
    return any(field in item for item in items)

def _build_insert_query(table_name: str, columns: list[str], values: str) -> str:
    """Build the final INSERT query string from table name, columns, and values."""
    return f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES {values};
    """

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
    """Generate an INSERT query string for one or more media roles."""
    if not media_roles:
        return ""
    
    has_media_role_id = _has_field_all(media_roles, "media_role_id")
    has_description = _has_field_any(media_roles, "description")
    has_is_active = _has_field_all(media_roles, "is_active")
    
    def get_media_role_values(role: dict) -> str:
        """Generate VALUES clause for a single media role"""
        values = []
        
        # Handle media_role_id (optional, only if all roles have it)
        if has_media_role_id:
            values.append(_format_sql_value(role["media_role_id"], "uuid"))
        
        # Required fields
        values.append(_format_sql_value(role["media_role_name"], "string"))
        
        # Handle description (optional, can be None)
        if has_description:
            values.append(_format_sql_value(role.get("description"), "nullable_string"))
        
        # Required fields
        values.append(_format_sql_value(role["sort_order"], "int"))
        
        # Handle is_active (optional, only if all roles have it)
        if has_is_active:
            values.append(_format_sql_value(role["is_active"], "bool"))
        
        # Required field
        values.append(_format_sql_value(role["media_role_code"], "string"))
        
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
    
    role_values = ", ".join(get_media_role_values(role) for role in media_roles)
    return _build_insert_query("media_roles", columns, role_values)

def insert_teams(teams: list[dict]) -> str:
    """Generate an INSERT query string for one or more teams."""
    if not teams:
        return ""
    
    has_team_id = _has_field_all(teams, "team_id")
    has_is_active = _has_field_all(teams, "is_active")
    
    def get_team_values(team: dict) -> str:
        """Generate VALUES clause for a single team"""
        values = []
        
        if has_team_id:
            values.append(_format_sql_value(team["team_id"], "uuid"))
        
        values.append(_format_sql_value(team["team_name"], "string"))
        
        if has_is_active:
            values.append(_format_sql_value(team["is_active"], "bool"))
        
        values.append(_format_sql_value(team["team_code"], "string"))
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_team_id:
        columns.append("team_id")
    columns.append("team_name")
    if has_is_active:
        columns.append("is_active")
    columns.append("team_code")
    
    team_values = ", ".join(get_team_values(team) for team in teams)
    return _build_insert_query("teams", columns, team_values)

def insert_users(users: list[dict]) -> str:
    """Generate an INSERT query string for one or more users."""
    if not users:
        return ""
    
    has_user_id = _has_field_all(users, "user_id")
    has_email = _has_field_any(users, "email")
    has_is_active = _has_field_all(users, "is_active")
    
    def get_user_values(user: dict) -> str:
        """Generate VALUES clause for a single user"""
        values = []
        
        if has_user_id:
            values.append(_format_sql_value(user["user_id"], "uuid"))
        
        values.append(_format_sql_value(user["first_name"], "string"))
        values.append(_format_sql_value(user["last_name"], "string"))
        
        if has_email:
            values.append(_format_sql_value(user.get("email"), "nullable_string"))
        
        values.append(_format_sql_value(user["phone"], "string"))
        
        if has_is_active:
            values.append(_format_sql_value(user["is_active"], "bool"))
        
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
    return _build_insert_query("users", columns, user_values)

def insert_team_users(team_users: list[dict]) -> str:
    """Generate an INSERT query string for one or more team_users."""
    if not team_users:
        return ""
    
    has_team_user_id = _has_field_all(team_users, "team_user_id")
    has_is_active = _has_field_all(team_users, "is_active")
    
    def get_team_user_values(team_user: dict) -> str:
        """Generate VALUES clause for a single team_user"""
        values = []
        
        if has_team_user_id:
            values.append(_format_sql_value(team_user["team_user_id"], "uuid"))
        
        values.append(_format_sql_value(team_user["team_id"], "uuid"))
        values.append(_format_sql_value(team_user["user_id"], "uuid"))
        
        if has_is_active:
            values.append(_format_sql_value(team_user["is_active"], "bool"))
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_team_user_id:
        columns.append("team_user_id")
    columns.append("team_id")
    columns.append("user_id")
    if has_is_active:
        columns.append("is_active")
    
    team_user_values = ", ".join(get_team_user_values(tu) for tu in team_users)
    return _build_insert_query("team_users", columns, team_user_values)

def insert_proficiency_levels(proficiency_levels: list[dict]) -> str:
    """Generate an INSERT query string for one or more proficiency levels."""
    if not proficiency_levels:
        return ""
    
    has_proficiency_level_id = _has_field_all(proficiency_levels, "proficiency_level_id")
    has_proficiency_level_number = _has_field_any(proficiency_levels, "proficiency_level_number")
    has_is_active = _has_field_all(proficiency_levels, "is_active")
    has_is_assignable = _has_field_all(proficiency_levels, "is_assignable")
    
    def get_proficiency_level_values(pl: dict) -> str:
        """Generate VALUES clause for a single proficiency level"""
        values = []
        
        if has_proficiency_level_id:
            values.append(_format_sql_value(pl["proficiency_level_id"], "uuid"))
        
        values.append(_format_sql_value(pl["proficiency_level_name"], "string"))
        
        if has_proficiency_level_number:
            values.append(_format_sql_value(pl.get("proficiency_level_number"), "int"))
        
        if has_is_active:
            values.append(_format_sql_value(pl["is_active"], "bool"))
        
        values.append(_format_sql_value(pl["proficiency_level_code"], "string"))
        
        if has_is_assignable:
            values.append(_format_sql_value(pl["is_assignable"], "bool"))
        
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
    return _build_insert_query("proficiency_levels", columns, pl_values)

def insert_user_roles(user_roles: list[dict]) -> str:
    """Generate an INSERT query string for one or more user_roles."""
    if not user_roles:
        return ""
    
    has_user_role_id = _has_field_all(user_roles, "user_role_id")
    
    def get_user_role_values(user_role: dict) -> str:
        """Generate VALUES clause for a single user_role"""
        values = []
        
        if has_user_role_id:
            values.append(_format_sql_value(user_role["user_role_id"], "uuid"))
        
        values.append(_format_sql_value(user_role["user_id"], "uuid"))
        values.append(_format_sql_value(user_role["media_role_id"], "uuid"))
        values.append(_format_sql_value(user_role["proficiency_level_id"], "uuid"))
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_user_role_id:
        columns.append("user_role_id")
    columns.append("user_id")
    columns.append("media_role_id")
    columns.append("proficiency_level_id")
    
    ur_values = ", ".join(get_user_role_values(ur) for ur in user_roles)
    return _build_insert_query("user_roles", columns, ur_values)

def insert_schedule_date_types(schedule_date_types: list[dict]) -> str:
    """Generate an INSERT query string for one or more schedule_date_types."""
    if not schedule_date_types:
        return ""
    
    has_schedule_date_type_id = _has_field_all(schedule_date_types, "schedule_date_type_id")
    has_is_active = _has_field_all(schedule_date_types, "is_active")
    
    def get_schedule_date_type_values(sdt: dict) -> str:
        """Generate VALUES clause for a single schedule_date_type"""
        values = []
        
        if has_schedule_date_type_id:
            values.append(_format_sql_value(sdt["schedule_date_type_id"], "uuid"))
        
        values.append(_format_sql_value(sdt["schedule_date_type_name"], "string"))
        
        if has_is_active:
            values.append(_format_sql_value(sdt["is_active"], "bool"))
        
        values.append(_format_sql_value(sdt["schedule_date_type_code"], "string"))
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_schedule_date_type_id:
        columns.append("schedule_date_type_id")
    columns.append("schedule_date_type_name")
    if has_is_active:
        columns.append("is_active")
    columns.append("schedule_date_type_code")
    
    sdt_values = ", ".join(get_schedule_date_type_values(sdt) for sdt in schedule_date_types)
    return _build_insert_query("schedule_date_types", columns, sdt_values)

def insert_schedules(schedules: list[dict]) -> str:
    """Generate an INSERT query string for one or more schedules."""
    if not schedules:
        return ""
    
    has_schedule_id = _has_field_all(schedules, "schedule_id")
    has_notes = _has_field_any(schedules, "notes")
    has_is_active = _has_field_all(schedules, "is_active")
    
    def get_schedule_values(schedule: dict) -> str:
        """Generate VALUES clause for a single schedule"""
        values = []
        
        if has_schedule_id:
            values.append(_format_sql_value(schedule["schedule_id"], "uuid"))
        
        values.append(_format_sql_value(schedule["month_start_date"], "date"))
        
        if has_notes:
            values.append(_format_sql_value(schedule.get("notes"), "nullable_string"))
        
        if has_is_active:
            values.append(_format_sql_value(schedule["is_active"], "bool"))
        
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
    return _build_insert_query("schedules", columns, schedule_values)

def insert_schedule_dates(schedule_dates: list[dict]) -> str:
    """Generate an INSERT query string for one or more schedule_dates."""
    if not schedule_dates:
        return ""
    
    has_schedule_date_id = _has_field_all(schedule_dates, "schedule_date_id")
    has_team_id = _has_field_any(schedule_dates, "team_id")
    has_notes = _has_field_any(schedule_dates, "notes")
    has_is_active = _has_field_all(schedule_dates, "is_active")
    
    def get_schedule_date_values(sd: dict) -> str:
        """Generate VALUES clause for a single schedule_date"""
        values = []
        
        if has_schedule_date_id:
            values.append(_format_sql_value(sd["schedule_date_id"], "uuid"))
        
        values.append(_format_sql_value(sd["schedule_id"], "uuid"))
        values.append(_format_sql_value(sd["date"], "date"))
        
        if has_team_id:
            if "team_id" in sd:
                values.append(_format_sql_value(sd["team_id"], "uuid"))
            else:
                values.append("NULL")
        
        values.append(_format_sql_value(sd["schedule_date_type_id"], "uuid"))
        
        if has_notes:
            values.append(_format_sql_value(sd.get("notes"), "nullable_string"))
        
        if has_is_active:
            values.append(_format_sql_value(sd["is_active"], "bool"))
        
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
    return _build_insert_query("schedule_dates", columns, sd_values)

def insert_schedule_date_roles(schedule_date_roles: list[dict]) -> str:
    """Generate an INSERT query string for one or more schedule_date_roles."""
    if not schedule_date_roles:
        return ""
    
    has_schedule_date_role_id = _has_field_all(schedule_date_roles, "schedule_date_role_id")
    has_is_required = _has_field_all(schedule_date_roles, "is_required")
    has_is_preferred = _has_field_all(schedule_date_roles, "is_preferred")
    has_assigned_user_id = _has_field_any(schedule_date_roles, "assigned_user_id")
    has_is_active = _has_field_all(schedule_date_roles, "is_active")
    
    def get_schedule_date_role_values(sdr: dict) -> str:
        """Generate VALUES clause for a single schedule_date_role"""
        values = []
        
        if has_schedule_date_role_id:
            values.append(_format_sql_value(sdr["schedule_date_role_id"], "uuid"))
        
        values.append(_format_sql_value(sdr["schedule_date_id"], "uuid"))
        values.append(_format_sql_value(sdr["media_role_id"], "uuid"))
        
        if has_is_required:
            values.append(_format_sql_value(sdr["is_required"], "bool"))
        
        if has_is_preferred:
            values.append(_format_sql_value(sdr["is_preferred"], "bool"))
        
        if has_assigned_user_id:
            values.append(_format_sql_value(sdr.get("assigned_user_id"), "uuid"))
        
        if has_is_active:
            values.append(_format_sql_value(sdr["is_active"], "bool"))
        
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
    return _build_insert_query("schedule_date_roles", columns, sdr_values)

def insert_user_dates(user_dates: list[dict]) -> str:
    """Generate an INSERT query string for one or more user_dates."""
    if not user_dates:
        return ""
    
    has_user_date_id = _has_field_all(user_dates, "user_date_id")
    
    def get_user_date_values(user_date: dict) -> str:
        """Generate VALUES clause for a single user_date"""
        values = []
        
        if has_user_date_id:
            values.append(_format_sql_value(user_date["user_date_id"], "uuid"))
        
        values.append(_format_sql_value(user_date["user_id"], "uuid"))
        values.append(_format_sql_value(user_date["date"], "date"))
        
        return f"({', '.join(values)})"
    
    columns = []
    if has_user_date_id:
        columns.append("user_date_id")
    columns.append("user_id")
    columns.append("date")
    
    ud_values = ", ".join(get_user_date_values(ud) for ud in user_dates)
    return _build_insert_query("user_dates", columns, ud_values)
    