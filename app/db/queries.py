import datetime
from uuid import UUID
from asyncpg import Connection
from pydantic import BaseModel
from app.utils.helpers import (
    get_date_details, 
    build_update_query, 
    build_insert_query, 
    build_where_clause,
    fetch_many, 
    fetch_single_row, 
    raise_bad_request_empty_payload,
    validate_table_name
)
from app.models import (
    MediaRoleCreate, MediaRoleUpdate,
    ProficiencyLevelCreate, ProficiencyLevelUpdate,
    ScheduleDateTypeCreate, ScheduleDateTypeUpdate,
    TeamCreate, TeamUpdate,
    UserCreate, UserUpdate,
    TeamUserCreate, TeamUserUpdate,
    UserRoleCreate, UserRoleUpdate,
    DateCreate, DateUpdate,
    ScheduleCreate, ScheduleUpdate,
    ScheduleDateCreate, ScheduleDateUpdate,
    ScheduleDateRoleCreate, ScheduleDateRoleUpdate,
    UserDateCreate, UserDateUpdate
)

# =============================
# GENERIC GETS AND DELETES
# =============================
async def fetch_all(
    conn: Connection,
    table: str,
    filters: dict[str, str | datetime.date] = None
) -> list[dict]:
    """
    Fetch all records from a table, optionally filtered.
    
    Args:
        conn: Database connection
        table: Table name (must be in VALID_TABLES whitelist)
        filters: Optional dictionary of column filters
        
    Returns:
        List of records as dictionaries
    """
    validate_table_name(table)
    if filters is None:
        filters = {}
    where_clause, converted_filters = build_where_clause(table, filters)
    query = f"SELECT * FROM {table}{where_clause};"
    rows = await fetch_many(conn, query, converted_filters)
    return [dict(row) for row in rows]

async def fetch_one(
    conn: Connection,
    table: str,
    filters: dict[str, str | datetime.date] = None
) -> dict:
    """
    Fetch a single record from a table, optionally filtered.
    
    Args:
        conn: Database connection
        table: Table name (must be in VALID_TABLES whitelist)
        filters: Optional dictionary of column filters
        
    Returns:
        Record as dictionary, or raises HTTPException(404) if not found
    """
    validate_table_name(table)
    if filters is None:
        filters = {}
    where_clause, converted_filters = build_where_clause(table, filters)
    query = f"SELECT * FROM {table}{where_clause};"
    row = await fetch_single_row(conn, query, converted_filters)
    return dict(row)

async def delete_all(
    conn: Connection,
    table: str,
    filters: dict[str, str | datetime.date] = None
) -> list[dict]:
    """
    Delete all records from a table matching the filters.
    
    Args:
        conn: Database connection
        table: Table name (must be in VALID_TABLES whitelist)
        filters: Optional dictionary of column filters
        
    Returns:
        List of deleted records as dictionaries
    """
    validate_table_name(table)
    if filters is None:
        filters = {}
    where_clause, converted_filters = build_where_clause(table, filters)
    query = f"DELETE FROM {table}{where_clause} RETURNING *;"
    rows = await fetch_many(conn, query, converted_filters)
    return [dict(row) for row in rows]

async def delete_one(
    conn: Connection,
    table: str,
    filters: dict[str, str | datetime.date] = None
) -> dict:
    """
    Delete a single record from a table matching the filters.
    
    Args:
        conn: Database connection
        table: Table name (must be in VALID_TABLES whitelist)
        filters: Optional dictionary of column filters
        
    Returns:
        Deleted record as dictionary, or raises HTTPException(404) if not found
    """
    validate_table_name(table)
    if filters is None:
        filters = {}
    where_clause, converted_filters = build_where_clause(table, filters)
    query = f"DELETE FROM {table}{where_clause} RETURNING *;"
    row = await fetch_single_row(conn, query, converted_filters)
    return dict(row)

# =============================
# GENERIC HELPERS
# =============================
async def _insert_record(conn: Connection, table: str, model: BaseModel) -> dict:
    """
    Generic helper for single record insertion.
    
    Args:
        conn: Database connection
        table: Table name (must be in VALID_TABLES whitelist)
        model: Pydantic model with data to insert
        
    Returns:
        Inserted record as dictionary
    """
    validate_table_name(table)
    data = model.model_dump(exclude_none=True)
    query, values = build_insert_query(table, [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def _update_record(
    conn: Connection,
    table: str,
    id_columns: dict[str, str | UUID | datetime.date],
    payload: BaseModel | None
) -> dict:
    """
    Generic helper for record updates.
    
    Args:
        conn: Database connection
        table: Table name (must be in VALID_TABLES whitelist)
        id_columns: Dictionary mapping ID column names to their values
        payload: Pydantic model with data to update (can be None if no updates provided)
        
    Returns:
        Updated record as dictionary, or raises HTTPException(404) if not found
        
    Raises:
        HTTPException(400): If payload is None or empty
    """
    validate_table_name(table)
    
    # Handle None payload (when request body is missing) - check before calling model_dump()
    if payload is None:
        raise_bad_request_empty_payload({})
    
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query(table, id_columns, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

# =============================
# MEDIA ROLES
# =============================
async def insert_media_role(conn: Connection, media_role: MediaRoleCreate) -> dict:
    return await _insert_record(conn, "media_roles", media_role)

async def update_media_role(conn: Connection, media_role_id: UUID, payload: MediaRoleUpdate) -> dict:
    return await _update_record(conn, "media_roles", {"media_role_id": media_role_id}, payload)

# =============================
# PROFICIENCY LEVELS
# =============================
async def insert_proficiency_level(conn: Connection, proficiency_level: ProficiencyLevelCreate) -> dict:
    return await _insert_record(conn, "proficiency_levels", proficiency_level)

async def update_proficiency_level(conn: Connection, proficiency_level_id: UUID, payload: ProficiencyLevelUpdate) -> dict:
    return await _update_record(conn, "proficiency_levels", {"proficiency_level_id": proficiency_level_id}, payload)

# =============================
# SCHEDULE DATE TYPES
# =============================
async def insert_schedule_date_type(conn: Connection, schedule_date_type: ScheduleDateTypeCreate) -> dict:
    return await _insert_record(conn, "schedule_date_types", schedule_date_type)

async def update_schedule_date_type(conn: Connection, schedule_date_type_id: UUID, payload: ScheduleDateTypeUpdate) -> dict:
    return await _update_record(conn, "schedule_date_types", {"schedule_date_type_id": schedule_date_type_id}, payload)

# =============================
# TEAMS
# =============================
async def insert_team(conn: Connection, team: TeamCreate) -> dict:
    return await _insert_record(conn, "teams", team)

async def update_team(conn: Connection, team_id: UUID, payload: TeamUpdate) -> dict:
    return await _update_record(conn, "teams", {"team_id": team_id}, payload)

# =============================
# USERS
# =============================
async def insert_user(conn: Connection, user: UserCreate) -> dict:
    return await _insert_record(conn, "users", user)

async def update_user(conn: Connection, user_id: UUID, payload: UserUpdate) -> dict:
    return await _update_record(conn, "users", {"user_id": user_id}, payload)

# =============================
# TEAM USERS
# =============================
async def insert_team_user(conn: Connection, team_user: TeamUserCreate) -> dict:
    return await _insert_record(conn, "team_users", team_user)

async def update_team_user(conn: Connection, team_id: UUID, user_id: UUID, payload: TeamUserUpdate) -> dict:
    return await _update_record(conn, "team_users", {"team_id": team_id, "user_id": user_id}, payload)

# =============================
# USER ROLES
# =============================
async def insert_user_role(conn: Connection, user_role: UserRoleCreate) -> dict:
    return await _insert_record(conn, "user_roles", user_role)

async def insert_all_roles_for_user(conn: Connection, user_id: UUID) -> list[dict]:
    """
    Insert all active media roles for a user with default 'untrained' proficiency level.
    
    This operation uses a transaction to ensure atomicity - either all roles are inserted
    or none are if an error occurs.
    
    Args:
        conn: Database connection (should be used within a transaction)
        user_id: UUID of the user
        
    Returns:
        List of inserted user role records
        
    Raises:
        ValueError: If default proficiency level 'untrained' is not found
    """
    # Use transaction to ensure atomicity of multiple operations
    async with conn.transaction():
        # Fetch all media roles
        # Inactive is included here because we want the record to be created even if the media role is inactive
        media_roles = await fetch_all(conn, table="media_roles")
    
        # Fetch the default 'untrained' proficiency level
        # Use fetch_all instead of fetch_one to avoid 404 HTTPException, so we can raise ValueError instead
        proficiency_levels = await fetch_all(conn, table="proficiency_levels", filters={"proficiency_level_code": "untrained"})
        if not proficiency_levels:
            raise ValueError("Default proficiency level 'untrained' not found")
        untrained_proficiency_id = proficiency_levels[0]["proficiency_level_id"]
        
        # Create data dictionaries for each media role
        user_roles_data = []
        for media_role in media_roles:
            user_roles_data.append({
                "user_id": user_id,
                "media_role_id": media_role["media_role_id"],
                "proficiency_level_id": untrained_proficiency_id
            })
        
        # Use bulk insert with ON CONFLICT to skip duplicates
        if not user_roles_data:
            return []
        
        query, values = build_insert_query("user_roles", user_roles_data)
        # Modify query to handle conflicts (skip duplicates)
        # Replace "RETURNING *;" with ON CONFLICT clause that also returns
        query = query.replace("RETURNING *;", "ON CONFLICT (user_id, media_role_id) DO NOTHING RETURNING *;")
        
        rows = await conn.fetch(query, *values)
        return [dict(row) for row in rows]

async def insert_all_users_for_role(conn: Connection, role_id: UUID) -> list[dict]:
    """
    Insert all users for a media role with default 'untrained' proficiency level.
    
    This operation uses a transaction to ensure atomicity - either all users are inserted
    or none are if an error occurs.
    
    Args:
        conn: Database connection (should be used within a transaction)
        role_id: UUID of the media role
        
    Returns:
        List of inserted user role records
        
    Raises:
        ValueError: If default proficiency level 'untrained' is not found
    """
    # Use transaction to ensure atomicity of multiple operations
    async with conn.transaction():
        # Fetch all users
        # All users are included here because we want the record to be created even if the user is inactive
        users = await fetch_all(conn, table="users")
        
        # Fetch the default 'untrained' proficiency level
        # Use fetch_all instead of fetch_one to avoid 404 HTTPException, so we can raise ValueError instead
        proficiency_levels = await fetch_all(conn, table="proficiency_levels", filters={"proficiency_level_code": "untrained"})
        if not proficiency_levels:
            raise ValueError("Default proficiency level 'untrained' not found")
        untrained_proficiency_id = proficiency_levels[0]["proficiency_level_id"]
        
        # Create data dictionaries for each user
        user_roles_data = []
        for user in users:
            user_roles_data.append({
                "user_id": user["user_id"],
                "media_role_id": role_id,
                "proficiency_level_id": untrained_proficiency_id
            })
        
        # Use bulk insert with ON CONFLICT to skip duplicates
        if not user_roles_data:
            return []
        
        query, values = build_insert_query("user_roles", user_roles_data)
        # Modify query to handle conflicts (skip duplicates)
        # Replace "RETURNING *;" with ON CONFLICT clause that also returns
        query = query.replace("RETURNING *;", "ON CONFLICT (user_id, media_role_id) DO NOTHING RETURNING *;")
        
        rows = await conn.fetch(query, *values)
        return [dict(row) for row in rows]

async def update_user_role(conn: Connection, user_id: UUID, role_id: UUID, payload: UserRoleUpdate) -> dict:
    return await _update_record(conn, "user_roles", {"user_id": user_id, "media_role_id": role_id}, payload)

# =============================
# DATES
# =============================
async def insert_date(conn: Connection, date_obj: DateCreate) -> dict:
    """
    Insert a date record with automatically calculated date details.
    
    Args:
        conn: Database connection
        date_obj: DateCreate model with the date to insert
        
    Returns:
        Inserted date record as dictionary
    """
    # DateCreate only has a mandatory 'date' field
    data = {"date": date_obj.date}
    # Automatically calculate and add other date details
    data.update(get_date_details(date_obj.date))
    query, values = build_insert_query("dates", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_date(conn: Connection, date: datetime.date, payload: DateUpdate) -> dict:
    return await _update_record(conn, "dates", {"date": date}, payload)

# =============================
# SCHEDULES
# =============================
async def insert_schedule(conn: Connection, schedule: ScheduleCreate) -> dict:
    return await _insert_record(conn, "schedules", schedule)

async def update_schedule(conn: Connection, schedule_id: UUID, payload: ScheduleUpdate) -> dict:
    return await _update_record(conn, "schedules", {"schedule_id": schedule_id}, payload)

# =============================
# SCHEDULE DATES
# =============================
async def insert_schedule_date(conn: Connection, schedule_date: ScheduleDateCreate) -> dict:
    return await _insert_record(conn, "schedule_dates", schedule_date)

async def update_schedule_date(conn: Connection, schedule_date_id: UUID, payload: ScheduleDateUpdate) -> dict:
    return await _update_record(conn, "schedule_dates", {"schedule_date_id": schedule_date_id}, payload)

# =============================
# SCHEDULE DATE ROLES
# =============================
async def insert_schedule_date_role(conn: Connection, schedule_date_role: ScheduleDateRoleCreate) -> dict:
    return await _insert_record(conn, "schedule_date_roles", schedule_date_role)

async def update_schedule_date_role(conn: Connection, schedule_date_role_id: UUID, payload: ScheduleDateRoleUpdate) -> dict:
    return await _update_record(conn, "schedule_date_roles", {"schedule_date_role_id": schedule_date_role_id}, payload)

# =============================
# USER DATES
# =============================
async def insert_user_date(conn: Connection, user_date: UserDateCreate) -> dict:
    return await _insert_record(conn, "user_dates", user_date)

async def insert_user_dates(
    conn: Connection, user_dates: list[UserDateCreate]
) -> list[dict]:
    """
    Insert multiple user date records in bulk.
    
    Args:
        conn: Database connection
        user_dates: List of UserDateCreate models to insert
        
    Returns:
        List of inserted user date records as dictionaries
    """
    # Convert all models to dicts for insertion
    data_list = [ud.model_dump(exclude_none=True) for ud in user_dates]
    query, values = build_insert_query("user_dates", data_list)
    rows = await conn.fetch(query, *values)
    return [dict(row) for row in rows]

async def update_user_date(conn: Connection, user_id: UUID, date: datetime.date, payload: UserDateUpdate) -> dict:
    return await _update_record(conn, "user_dates", {"user_id": user_id, "date": date}, payload)
