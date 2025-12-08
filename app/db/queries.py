from datetime import date
from asyncpg import Connection
from app.utils.helpers import table_id, convert_id_for_table, get_date_details
from app.models import MediaRoleCreate, ProficiencyLevelCreate, ScheduleDateTypeCreate, TeamCreate, UserCreate, TeamUserCreate, UserRoleCreate, DateCreate, ScheduleCreate, ScheduleDateCreate, ScheduleDateRoleCreate, UserAvailabilityCreate

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
    query = """
    INSERT INTO media_roles (media_role_name, description, sort_order, is_active, media_role_code)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        media_role.media_role_name,
        media_role.description,
        media_role.sort_order,
        media_role.is_active if media_role.is_active is not None else True,
        media_role.media_role_code
    )
    return dict(row)

async def insert_proficiency_level(conn: Connection, proficiency_level: ProficiencyLevelCreate) -> dict:
    query = """
    INSERT INTO proficiency_levels (proficiency_level_name, proficiency_level_number, is_active, proficiency_level_code, is_assignable)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        proficiency_level.proficiency_level_name,
        proficiency_level.proficiency_level_number,
        proficiency_level.is_active if proficiency_level.is_active is not None else True,
        proficiency_level.proficiency_level_code,
        proficiency_level.is_assignable if proficiency_level.is_assignable is not None else False
    )
    return dict(row)

async def insert_schedule_date_type(conn: Connection, schedule_date_type: ScheduleDateTypeCreate) -> dict:
    query = """
    INSERT INTO schedule_date_types (schedule_date_type_name, is_active, schedule_date_type_code)
    VALUES ($1, $2, $3)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        schedule_date_type.schedule_date_type_name,
        schedule_date_type.is_active if schedule_date_type.is_active is not None else True,
        schedule_date_type.schedule_date_type_code
    )
    return dict(row)

async def insert_team(conn: Connection, team: TeamCreate) -> dict:
    query = """
    INSERT INTO teams (team_name, team_code, is_active)
    VALUES ($1, $2, $3)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        team.team_name,
        team.team_code,
        team.is_active if team.is_active is not None else True
    )
    return dict(row)

async def insert_user(conn: Connection, user: UserCreate) -> dict:
    query = """
    INSERT INTO users (first_name, last_name, email, phone, is_active)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        user.first_name,
        user.last_name,
        user.email,
        user.phone,
        user.is_active if user.is_active is not None else True
    )
    return dict(row)

async def insert_team_user(conn: Connection, team_user: TeamUserCreate) -> dict:
    query = """
    INSERT INTO team_users (team_id, user_id, is_active)
    VALUES ($1, $2, $3)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        team_user.team_id,
        team_user.user_id,
        team_user.is_active if team_user.is_active is not None else True
    )
    return dict(row)

async def insert_user_role(conn: Connection, user_role: UserRoleCreate) -> dict:
    query = """
    INSERT INTO user_roles (user_id, media_role_id, proficiency_level_id)
    VALUES ($1, $2, $3)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        user_role.user_id,
        user_role.media_role_id,
        user_role.proficiency_level_id
    )
    return dict(row)

async def insert_date(conn: Connection, date_obj: DateCreate) -> dict:
    query = """
    INSERT INTO dates (
        date,
        calendar_year,
        calendar_month,
        month_name,
        month_abbr,
        calendar_day,
        weekday,
        weekday_name,
        is_weekend,
        is_weekday,
        is_holiday,
        week_number,
        is_first_of_month,
        is_last_of_month,
        calendar_quarter,
        weekday_of_month
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
    RETURNING *;
    """
    date_details = get_date_details(date_obj.date)
    row = await conn.fetchrow(
        query,
        date_obj.date,
        date_details["calendar_year"],
        date_details["calendar_month"],
        date_details["month_name"],
        date_details["month_abbr"],
        date_details["calendar_day"],
        date_details["weekday"],
        date_details["weekday_name"],
        date_details["is_weekend"],
        date_details["is_weekday"],
        date_details["is_holiday"],
        date_details["week_number"],
        date_details["is_first_of_month"],
        date_details["is_last_of_month"],
        date_details["calendar_quarter"],
        date_details["weekday_of_month"]
    )
    return dict(row)

async def insert_schedule(conn: Connection, schedule: ScheduleCreate) -> dict:
    query = """
    INSERT INTO schedules (month_start_date, is_active, notes)
    VALUES ($1, $2, $3)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        schedule.month_start_date,
        schedule.is_active if schedule.is_active is not None else True,
        schedule.notes
    )
    return dict(row)

async def insert_schedule_date(conn: Connection, schedule_date: ScheduleDateCreate) -> dict:
    query = """
    INSERT INTO schedule_dates (schedule_id, date, team_id, schedule_date_type_id, notes, is_active)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        schedule_date.schedule_id,
        schedule_date.date,
        schedule_date.team_id,
        schedule_date.schedule_date_type_id,
        schedule_date.notes,
        schedule_date.is_active if schedule_date.is_active is not None else True
    )
    return dict(row)

async def insert_schedule_date_role(conn: Connection, schedule_date_role: ScheduleDateRoleCreate) -> dict:
    query = """
    INSERT INTO schedule_date_roles (schedule_date_id, media_role_id, is_required, is_preferred, assigned_user_id, is_active)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        schedule_date_role.schedule_date_id,
        schedule_date_role.media_role_id,
        schedule_date_role.is_required if schedule_date_role.is_required is not None else False,
        schedule_date_role.is_preferred if schedule_date_role.is_preferred is not None else False,
        schedule_date_role.assigned_user_id,
        schedule_date_role.is_active if schedule_date_role.is_active is not None else True
    )
    return dict(row)

async def insert_user_availability(conn: Connection, user_availability: UserAvailabilityCreate) -> dict:
    query = """
    INSERT INTO user_availability (user_id, date)
    VALUES ($1, $2)
    RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        user_availability.user_id,
        user_availability.date
    )
    return dict(row)

# =============================
# UPDATES
# =============================