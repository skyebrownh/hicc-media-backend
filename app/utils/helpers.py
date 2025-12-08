import datetime

# Return the primary key column name for a given table
def table_id(table: str) -> str:
    if table == "dates":
        return "date"

    return f"{table[0:len(table) - 1] if table.endswith("s") else table}_id"

# Convert id to a date object if the table is 'dates'
def convert_id_for_table(table: str, id: str | datetime.date) -> str | datetime.date:
    if table == "dates" and isinstance(id, str):
        return datetime.date.fromisoformat(id)  # Convert ISO string to date object
    return id

# Return a dict of detailed date information
def get_date_details(date: datetime.date) -> dict:
    return {
        "calendar_year": date.year,
        "calendar_month": date.month,
        "month_name": date.strftime("%B"),
        "month_abbr": date.strftime("%b"),
        "calendar_day": date.day,
        "weekday": date.weekday(),
        "weekday_name": date.strftime("%A"),
        "is_weekend": date.weekday() >= 5,
        "is_weekday": date.weekday() < 5,
        "is_holiday": False,
        "week_number": int(date.strftime("%U")),
        "is_first_of_month": date.day == 1,
        "is_last_of_month": (date + datetime.timedelta(days=1)).month != date.month,
        "calendar_quarter": (date.month - 1) // 3 + 1,
        "weekday_of_month": (date.day - 1) // 7 + 1
    }