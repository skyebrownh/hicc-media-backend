from datetime import date
from asyncpg import Connection
from app.utils.helpers import table_id, convert_id_for_table, get_date_details, build_update_query, build_insert_query
from app.models import MediaRoleCreate, ProficiencyLevelCreate, ScheduleDateTypeCreate, TeamCreate, UserCreate, TeamUserCreate, UserRoleCreate, DateCreate, ScheduleCreate, ScheduleDateCreate, ScheduleDateRoleCreate, UserAvailabilityCreate
from app.models import MediaRoleUpdate, ProficiencyLevelUpdate, ScheduleDateTypeUpdate, TeamUpdate, UserUpdate, TeamUserUpdate, UserRoleUpdate, DateUpdate, ScheduleUpdate, ScheduleDateUpdate, ScheduleDateRoleUpdate, UserAvailabilityUpdate

# =============================
# GETS AND DELETES
# =============================
async def fetch_all(conn: Connection, table: str) -> list[dict]:
    query = f"SELECT * FROM {table};"
    rows = await conn.fetch(query)
    return [dict(row) for row in rows]

async def fetch_one(conn: Connection, table: str, id: str | date) -> dict | None:
    id = convert_id_for_table(table, id)
    query = f"SELECT * FROM {table} WHERE {table_id(table)} = $1;"
    row = await conn.fetchrow(query, id)
    return dict(row) if row else None

async def delete_one(conn: Connection, table: str, id: str | date) -> dict | None:
    id = convert_id_for_table(table, id)
    query = f"DELETE FROM {table} WHERE {table_id(table)} = $1 RETURNING *;"
    row = await conn.fetchrow(query, id)
    return dict(row) if row else None

# =============================
# INSERTS
# =============================
async def insert_media_role(conn: Connection, media_role: MediaRoleCreate) -> dict:
    data = media_role.model_dump(exclude_none=True)
    query, values = build_insert_query("media_roles", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_proficiency_level(conn: Connection, proficiency_level: ProficiencyLevelCreate) -> dict:
    data = proficiency_level.model_dump(exclude_none=True)
    query, values = build_insert_query("proficiency_levels", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_schedule_date_type(conn: Connection, schedule_date_type: ScheduleDateTypeCreate) -> dict:
    data = schedule_date_type.model_dump(exclude_none=True)
    query, values = build_insert_query("schedule_date_types", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_team(conn: Connection, team: TeamCreate) -> dict:
    data = team.model_dump(exclude_none=True)
    query, values = build_insert_query("teams", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_user(conn: Connection, user: UserCreate) -> dict:
    data = user.model_dump(exclude_none=True)
    query, values = build_insert_query("users", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_team_user(conn: Connection, team_user: TeamUserCreate) -> dict:
    data = team_user.model_dump(exclude_none=True)
    query, values = build_insert_query("team_users", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_user_role(conn: Connection, user_role: UserRoleCreate) -> dict:
    data = user_role.model_dump(exclude_none=True)
    query, values = build_insert_query("user_roles", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_date(conn: Connection, date_obj: DateCreate) -> dict:
    data = date_obj.model_dump(exclude_none=True)
    query, values = build_insert_query("dates", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_schedule(conn: Connection, schedule: ScheduleCreate) -> dict:
    data = schedule.model_dump(exclude_none=True)
    query, values = build_insert_query("schedules", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_schedule_date(conn: Connection, schedule_date: ScheduleDateCreate) -> dict:
    data = schedule_date.model_dump(exclude_none=True)
    query, values = build_insert_query("schedule_dates", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_schedule_date_role(conn: Connection, schedule_date_role: ScheduleDateRoleCreate) -> dict:
    data = schedule_date_role.model_dump(exclude_none=True)
    query, values = build_insert_query("schedule_date_roles", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

async def insert_user_availability(conn: Connection, user_availability: UserAvailabilityCreate) -> dict:
    data = user_availability.model_dump(exclude_none=True)
    query, values = build_insert_query("user_availability", data)
    row = await conn.fetchrow(query, *values)
    return dict(row)

# =============================
# UPDATES
# =============================
async def update_media_role(conn: Connection, media_role_id: str, payload: MediaRoleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    # Use the helper function to build the query and values
    query, values = build_update_query("media_roles", "media_role_id", media_role_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_proficiency_level(conn: Connection, proficiency_level_id: str, payload: ProficiencyLevelUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("proficiency_levels", "proficiency_level_id", proficiency_level_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_schedule_date_type(conn: Connection, schedule_date_type_id: str, payload: ScheduleDateTypeUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("schedule_date_types", "schedule_date_type_id", schedule_date_type_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_team(conn: Connection, team_id: str, payload: TeamUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("teams", "team_id", team_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_user(conn: Connection, user_id: str, payload: UserUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("users", "user_id", user_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_team_user(conn: Connection, team_user_id: str, payload: TeamUserUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("team_users", "team_user_id", team_user_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_user_role(conn: Connection, user_role_id: str, payload: UserRoleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("user_roles", "user_role_id", user_role_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_date(conn: Connection, date: str, payload: DateUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("dates", "date", date, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_schedule(conn: Connection, schedule_id: str, payload: ScheduleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("schedules", "schedule_id", schedule_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_schedule_date(conn: Connection, schedule_date_id: str, payload: ScheduleDateUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("schedule_dates", "schedule_date_id", schedule_date_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_schedule_date_role(conn: Connection, schedule_date_role_id: str, payload: ScheduleDateRoleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("schedule_date_roles", "schedule_date_role_id", schedule_date_role_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

async def update_user_availability(conn: Connection, user_availability_id: str, payload: UserAvailabilityUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True)

    if not data:
        return None  # Nothing to update, TODO: error handling and logging

    query, values = build_update_query("user_availability", "user_availability_id", user_availability_id, data)

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None