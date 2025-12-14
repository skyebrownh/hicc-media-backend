import datetime
from uuid import UUID
from asyncpg import Connection
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
# GETS AND DELETES
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
# INSERTS
# =============================
async def insert_media_role(conn: Connection, media_role: MediaRoleCreate) -> dict:
    data = media_role.model_dump(exclude_none=True)
    query, values = build_insert_query("media_roles", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_proficiency_level(conn: Connection, proficiency_level: ProficiencyLevelCreate) -> dict:
    data = proficiency_level.model_dump(exclude_none=True)
    query, values = build_insert_query("proficiency_levels", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_schedule_date_type(conn: Connection, schedule_date_type: ScheduleDateTypeCreate) -> dict:
    data = schedule_date_type.model_dump(exclude_none=True)
    query, values = build_insert_query("schedule_date_types", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_team(conn: Connection, team: TeamCreate) -> dict:
    data = team.model_dump(exclude_none=True)
    query, values = build_insert_query("teams", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_user(conn: Connection, user: UserCreate) -> dict:
    data = user.model_dump(exclude_none=True)
    query, values = build_insert_query("users", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_team_user(conn: Connection, team_user: TeamUserCreate) -> dict:
    data = team_user.model_dump(exclude_none=True)
    query, values = build_insert_query("team_users", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_user_role(conn: Connection, user_role: UserRoleCreate) -> dict:
    data = user_role.model_dump(exclude_none=True)
    query, values = build_insert_query("user_roles", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_date(conn: Connection, date_obj: DateCreate) -> dict:
    # DateCreate only has a mandatory 'date' field
    data = {"date": date_obj.date}
    # Automatically calculate and add other date details
    data.update(get_date_details(date_obj.date))
    query, values = build_insert_query("dates", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_schedule(conn: Connection, schedule: ScheduleCreate) -> dict:
    data = schedule.model_dump(exclude_none=True)
    query, values = build_insert_query("schedules", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_schedule_date(conn: Connection, schedule_date: ScheduleDateCreate) -> dict:
    data = schedule_date.model_dump(exclude_none=True)
    query, values = build_insert_query("schedule_dates", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_schedule_date_role(conn: Connection, schedule_date_role: ScheduleDateRoleCreate) -> dict:
    data = schedule_date_role.model_dump(exclude_none=True)
    query, values = build_insert_query("schedule_date_roles", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_user_date(conn: Connection, user_date: UserDateCreate) -> dict:
    data = user_date.model_dump(exclude_none=True)
    query, values = build_insert_query("user_dates", [data])
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def insert_user_dates(
    conn: Connection, user_dates: list[UserDateCreate]
) -> list[dict]:
    # Convert all models to dicts for insertion
    data_list = [ud.model_dump(exclude_none=True) for ud in user_dates]
    query, values = build_insert_query("user_dates", data_list)
    rows = await conn.fetch(query, *values)
    return [dict(row) for row in rows]

# =============================
# UPDATES
# =============================
async def update_media_role(conn: Connection, media_role_id: str, payload: MediaRoleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("media_roles", {"media_role_id": media_role_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_proficiency_level(conn: Connection, proficiency_level_id: str, payload: ProficiencyLevelUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("proficiency_levels", {"proficiency_level_id": proficiency_level_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_schedule_date_type(conn: Connection, schedule_date_type_id: str, payload: ScheduleDateTypeUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("schedule_date_types", {"schedule_date_type_id": schedule_date_type_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_team(conn: Connection, team_id: str, payload: TeamUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("teams", {"team_id": team_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_user(conn: Connection, user_id: str, payload: UserUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("users", {"user_id": user_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_team_user(conn: Connection, team_id: UUID, user_id: UUID, payload: TeamUserUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("team_users", {"team_id": team_id, "user_id": user_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_user_role(conn: Connection, user_role_id: str, payload: UserRoleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("user_roles", {"user_role_id": user_role_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_date(conn: Connection, date: str, payload: DateUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("dates", {"date": date}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_schedule(conn: Connection, schedule_id: str, payload: ScheduleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("schedules", {"schedule_id": schedule_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_schedule_date(conn: Connection, schedule_date_id: str, payload: ScheduleDateUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("schedule_dates", {"schedule_date_id": schedule_date_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_schedule_date_role(conn: Connection, schedule_date_role_id: str, payload: ScheduleDateRoleUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("schedule_date_roles", {"schedule_date_role_id": schedule_date_role_id}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)

async def update_user_date(conn: Connection, user_id: UUID, date: datetime.date, payload: UserDateUpdate) -> dict | None:
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    raise_bad_request_empty_payload(data)
    query, values = build_update_query("user_dates", {"user_id": user_id, "date": date}, data)
    row = await fetch_single_row(conn, query, values)
    return dict(row)