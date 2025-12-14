import datetime
from app.utils.helpers import get_date_details

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
    