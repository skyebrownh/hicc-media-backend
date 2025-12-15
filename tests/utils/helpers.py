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
    