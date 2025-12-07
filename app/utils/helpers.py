from datetime import date

# Return the primary key column name for a given table
def table_id(table: str) -> str:
    if table == "dates":
        return "date"

    return f"{table[0:len(table) - 1] if table.endswith("s") else table}_id"

# Convert id to a date object if the table is 'dates'
def convert_id_for_table(table: str, id: str | date) -> str | date:
    if table == "dates" and isinstance(id, str):
        return date.fromisoformat(id)  # Convert ISO string to date object
    return id