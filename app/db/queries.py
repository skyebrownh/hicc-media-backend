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
    raise_bad_request_empty_payload
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
) -> dict | None:
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
) -> dict | None:
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
    """Generic helper for single record insertion."""
    data = model.model_dump(exclude_none=True)
    query, values = build_insert_query(table, [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def _update_record(
    conn: Connection,
    table: str,
    id_columns: dict[str, str | UUID | datetime.date],
    payload: BaseModel
) -> dict | None:
    """Generic helper for record updates."""
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

async def update_media_role(conn: Connection, media_role_id: str, payload: MediaRoleUpdate) -> dict | None:
    return await _update_record(conn, "media_roles", {"media_role_id": media_role_id}, payload)

# =============================
# PROFICIENCY LEVELS
# =============================
async def insert_proficiency_level(conn: Connection, proficiency_level: ProficiencyLevelCreate) -> dict:
    return await _insert_record(conn, "proficiency_levels", proficiency_level)

async def update_proficiency_level(conn: Connection, proficiency_level_id: str, payload: ProficiencyLevelUpdate) -> dict | None:
    return await _update_record(conn, "proficiency_levels", {"proficiency_level_id": proficiency_level_id}, payload)

# =============================
# SCHEDULE DATE TYPES
# =============================
async def insert_schedule_date_type(conn: Connection, schedule_date_type: ScheduleDateTypeCreate) -> dict:
    return await _insert_record(conn, "schedule_date_types", schedule_date_type)

async def update_schedule_date_type(conn: Connection, schedule_date_type_id: str, payload: ScheduleDateTypeUpdate) -> dict | None:
    return await _update_record(conn, "schedule_date_types", {"schedule_date_type_id": schedule_date_type_id}, payload)

# =============================
# TEAMS
# =============================
async def insert_team(conn: Connection, team: TeamCreate) -> dict:
    return await _insert_record(conn, "teams", team)

async def update_team(conn: Connection, team_id: str, payload: TeamUpdate) -> dict | None:
    return await _update_record(conn, "teams", {"team_id": team_id}, payload)

# =============================
# USERS
# =============================
async def insert_user(conn: Connection, user: UserCreate) -> dict:
    return await _insert_record(conn, "users", user)

async def update_user(conn: Connection, user_id: str, payload: UserUpdate) -> dict | None:
    return await _update_record(conn, "users", {"user_id": user_id}, payload)

# =============================
# TEAM USERS
# =============================
async def insert_team_user(conn: Connection, team_user: TeamUserCreate) -> dict:
    return await _insert_record(conn, "team_users", team_user)

async def update_team_user(conn: Connection, team_id: UUID, user_id: UUID, payload: TeamUserUpdate) -> dict | None:
    return await _update_record(conn, "team_users", {"team_id": team_id, "user_id": user_id}, payload)

# =============================
# USER ROLES
# =============================
async def insert_user_role(conn: Connection, user_role: UserRoleCreate) -> dict:
    return await _insert_record(conn, "user_roles", user_role)

async def insert_all_roles_for_user(conn: Connection, user_id: UUID) -> list[dict]:
    """Insert all active media roles for a user with default 'untrained' proficiency level."""
    # Fetch all  media roles
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
    """Insert all users for a media role with default 'untrained' proficiency level."""
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

async def update_user_role(conn: Connection, user_id: UUID, role_id: UUID, payload: UserRoleUpdate) -> dict | None:
    return await _update_record(conn, "user_roles", {"user_id": user_id, "media_role_id": role_id}, payload)

# =============================
# DATES
# =============================
async def insert_date(conn: Connection, date_obj: DateCreate) -> dict:
    # DateCreate only has a mandatory 'date' field
    data = {"date": date_obj.date}
    # Automatically calculate and add other date details
    data.update(get_date_details(date_obj.date))
    query, values = build_insert_query("dates", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_date(conn: Connection, date: str, payload: DateUpdate) -> dict | None:
    return await _update_record(conn, "dates", {"date": date}, payload)

# =============================
# SCHEDULES
# =============================
async def insert_schedule(conn: Connection, schedule: ScheduleCreate) -> dict:
    return await _insert_record(conn, "schedules", schedule)

async def update_schedule(conn: Connection, schedule_id: str, payload: ScheduleUpdate) -> dict | None:
    return await _update_record(conn, "schedules", {"schedule_id": schedule_id}, payload)

# =============================
# SCHEDULE DATES
# =============================
async def insert_schedule_date(conn: Connection, schedule_date: ScheduleDateCreate) -> dict:
    return await _insert_record(conn, "schedule_dates", schedule_date)

async def update_schedule_date(conn: Connection, schedule_date_id: str, payload: ScheduleDateUpdate) -> dict | None:
    return await _update_record(conn, "schedule_dates", {"schedule_date_id": schedule_date_id}, payload)

# =============================
# SCHEDULE DATE ROLES
# =============================
async def insert_schedule_date_role(conn: Connection, schedule_date_role: ScheduleDateRoleCreate) -> dict:
    return await _insert_record(conn, "schedule_date_roles", schedule_date_role)

async def update_schedule_date_role(conn: Connection, schedule_date_role_id: str, payload: ScheduleDateRoleUpdate) -> dict | None:
    return await _update_record(conn, "schedule_date_roles", {"schedule_date_role_id": schedule_date_role_id}, payload)

# =============================
# USER DATES
# =============================
async def insert_user_date(conn: Connection, user_date: UserDateCreate) -> dict:
    return await _insert_record(conn, "user_dates", user_date)

async def insert_user_dates(
    conn: Connection, user_dates: list[UserDateCreate]
) -> list[dict]:
    # Convert all models to dicts for insertion
    data_list = [ud.model_dump(exclude_none=True) for ud in user_dates]
    query, values = build_insert_query("user_dates", data_list)
    rows = await conn.fetch(query, *values)
    return [dict(row) for row in rows]

async def update_user_date(conn: Connection, user_id: UUID, date: datetime.date, payload: UserDateUpdate) -> dict | None:
    return await _update_record(conn, "user_dates", {"user_id": user_id, "date": date}, payload)
