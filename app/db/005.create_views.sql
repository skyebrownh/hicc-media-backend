-- =============================
-- V_TEAM_USERS
-- =============================
CREATE OR REPLACE VIEW public.v_team_users AS
SELECT
    tu.team_user_id,
    tu.team_id,
    tu.user_id,
    tu.is_active,
    t.team_name,
    t.team_code,
    t.is_active AS team_is_active,
    u.first_name,
    u.last_name,
    u.email,
    u.phone,
    u.is_active AS user_is_active
FROM public.team_users tu
JOIN public.teams t ON tu.team_id = t.team_id
JOIN public.users u ON tu.user_id = u.user_id;


-- =============================
-- V_USER_ROLES
-- =============================
CREATE OR REPLACE VIEW public.v_user_roles AS
SELECT
    ur.user_role_id,
    ur.user_id,
    ur.media_role_id,
    ur.proficiency_level_id,
    u.first_name,
    u.last_name,
    u.email,
    u.phone,
    u.is_active AS user_is_active,
    m.media_role_name,
    m.media_role_code,
    m.sort_order,
    m.is_active AS media_role_is_active,
    p.proficiency_level_name,
    p.proficiency_level_number,
    p.proficiency_level_code,
    p.is_assignable,
    p.is_active AS proficiency_level_is_active
FROM public.user_roles ur
JOIN public.users u ON ur.user_id = u.user_id
JOIN public.media_roles m ON ur.media_role_id = m.media_role_id
JOIN public.proficiency_levels p ON ur.proficiency_level_id = p.proficiency_level_id;


-- =============================
-- V_SCHEDULE_DATES
-- =============================
CREATE OR REPLACE VIEW public.v_schedule_dates AS
SELECT
    sd.schedule_date_id,
    sd.schedule_id,
    sd.date,
    sd.schedule_date_type_id,
    sd.team_id,
    sd.notes,
    sd.is_active,
    s.month_start_date,
    s.notes AS schedule_notes,
    s.is_active AS schedule_is_active,
    sdt.schedule_date_type_name,
    sdt.schedule_date_type_code,
    sdt.is_active AS schedule_date_type_is_active,
    t.team_name,
    t.team_code,
    t.is_active AS team_is_active,
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    d.month_abbr,
    d.calendar_day,
    d.weekday,
    d.weekday_name,
    d.week_number,
    d.calendar_quarter,
    d.weekday_of_month
FROM public.schedule_dates sd
JOIN public.schedules s ON sd.schedule_id = s.schedule_id
JOIN public.schedule_date_types sdt ON sd.schedule_date_type_id = sdt.schedule_date_type_id
LEFT JOIN public.teams t ON sd.team_id = t.team_id
JOIN public.dates d ON sd.date = d.date;



-- =============================
-- V_SCHEDULE_DATE_ROLES
-- =============================
CREATE OR REPLACE VIEW public.v_schedule_date_roles AS
SELECT
    sdr.schedule_date_role_id,
    sdr.schedule_date_id,
    sdr.media_role_id,
    sdr.is_required,
    sdr.is_preferred,
    sdr.assigned_user_id,
    sdr.is_active,
    v_sd.schedule_id,
    v_sd.date,
    v_sd.schedule_date_type_id,
    v_sd.team_id,
    v_sd.notes AS schedule_date_notes,
    v_sd.is_active AS schedule_date_is_active,
    v_sd.month_start_date,
    v_sd.schedule_notes,
    v_sd.schedule_is_active,
    v_sd.schedule_date_type_name,
    v_sd.schedule_date_type_code,
    v_sd.schedule_date_type_is_active,
    v_sd.team_name,
    v_sd.team_code,
    v_sd.team_is_active,
    v_sd.calendar_year,
    v_sd.calendar_month,
    v_sd.month_name,
    v_sd.month_abbr,
    v_sd.calendar_day,
    v_sd.weekday,
    v_sd.weekday_name,
    v_sd.week_number,
    v_sd.calendar_quarter,
    v_sd.weekday_of_month,
    m.media_role_name,
    m.media_role_code,
    m.sort_order,
    m.is_active AS media_role_is_active,
    u.first_name AS assigned_user_first_name,
    u.last_name AS assigned_user_last_name,
    u.email AS assigned_user_email,
    u.phone AS assigned_user_phone,
    u.is_active AS assigned_user_is_active
FROM public.schedule_date_roles sdr
JOIN public.v_schedule_dates v_sd ON sdr.schedule_date_id = v_sd.schedule_date_id
JOIN public.media_roles m ON sdr.media_role_id = m.media_role_id
LEFT JOIN public.users u ON sdr.assigned_user_id = u.user_id;



-- =============================
-- V_USER_AVAILABILITY
-- =============================
CREATE OR REPLACE VIEW public.v_user_availability AS
SELECT
    ua.user_availability_id,
    ua.user_id,
    ua.date,
    u.first_name,
    u.last_name,
    u.email,
    u.phone,
    u.is_active AS user_is_active,
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    d.month_abbr,
    d.calendar_day,
    d.weekday,
    d.weekday_name,
    d.week_number,
    d.calendar_quarter,
    d.weekday_of_month
FROM public.user_availability ua
JOIN public.users u ON ua.user_id = u.user_id
JOIN public.dates d ON ua.date = d.date;