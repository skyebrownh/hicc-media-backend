-- =============================
-- DATES
-- =============================
INSERT INTO public.dates (
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
    week_number,
    is_first_of_month,
    is_last_of_month,
    calendar_quarter,
    weekday_of_month
)
SELECT
    d::date AS date,
    EXTRACT(YEAR FROM d)::int AS calendar_year,
    EXTRACT(MONTH FROM d)::int AS calendar_month,
    TO_CHAR(d, 'Month')::text AS month_name,
    TO_CHAR(d, 'Mon')::text AS month_abbr,
    EXTRACT(DAY FROM d)::int AS calendar_day,
    EXTRACT(DOW FROM d)::int AS weekday,
    TO_CHAR(d, 'Day')::text AS weekday_name,
    (EXTRACT(DOW FROM d) IN (0, 6)) AS is_weekend,
    (EXTRACT(DOW FROM d) NOT IN (0, 6)) AS is_weekday,
    EXTRACT(WEEK FROM d)::int AS week_number,
    (d = DATE_TRUNC('month', d)::date) AS is_first_of_month,
    (d = (DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day')::date) AS is_last_of_month,
    EXTRACT(QUARTER FROM d)::int AS calendar_quarter,
    (
        1 + EXTRACT(WEEK FROM d) 
        - EXTRACT(WEEK FROM date_trunc('month', d)::date)
    )::int AS weekday_of_month
FROM generate_series(
    '2025-01-01'::date,
    '2026-12-31'::date,
    INTERVAL '1 day'
) AS g(d);

-- =============================
-- SCHEDULES
-- =============================
INSERT INTO public.schedules (schedule_id, month_start_date, notes, is_active)
SELECT gen_random_uuid(), d.date, null, true
FROM public.dates d
WHERE d.is_first_of_month = true;

-- =============================
-- SCHEDULE DATES
-- =============================
INSERT INTO public.schedule_dates (schedule_date_id, schedule_id, date, team_id, schedule_date_type_id, notes, is_active)
SELECT gen_random_uuid(), s.schedule_id, d.date, 
    CASE 
        WHEN d.weekday_of_month IN (1, 3) THEN t_alpha.team_id
        WHEN d.weekday_of_month IN (2, 4) THEN t_omega.team_id
        ELSE NULL
    END AS team_id,
    sdt.schedule_date_type_id, null, true
FROM public.schedules s
JOIN public.dates d 
    ON d.calendar_month = DATE_PART('month', s.month_start_date)
   AND d.calendar_year = DATE_PART('year', s.month_start_date)
JOIN public.schedule_date_types sdt 
    ON sdt.schedule_date_type_code = 'service'
JOIN public.teams t_alpha 
    ON t_alpha.team_code = 'alpha'
JOIN public.teams t_omega 
    ON t_omega.team_code = 'omega'
WHERE d.weekday IN (0, 3); -- 0 = Sunday, 3 = Wednesday

INSERT INTO public.schedule_dates (schedule_date_id, schedule_id, date, team_id, schedule_date_type_id, notes, is_active)
SELECT gen_random_uuid(), s.schedule_id, d.date, 
    NULL as team_id,
    sdt.schedule_date_type_id, null, true
FROM public.schedules s
JOIN public.dates d 
    ON d.calendar_month = DATE_PART('month', s.month_start_date)
   AND d.calendar_year = DATE_PART('year', s.month_start_date)
JOIN public.schedule_date_types sdt 
    ON sdt.schedule_date_type_code = 'prayer'
WHERE d.weekday = 6; -- 6 = Saturday

-- Load CSV data into a temporary table
CREATE TABLE temp_schedule_dates_csv (
    date TEXT,
    team TEXT,
    notes TEXT
);

-- TODO: Run pgAdmin Import to load data from CSV file into the temporary table (update only)
-- update notes for existing rows based on CSV data
UPDATE public.schedule_dates sd
SET notes = seed.notes
FROM (
    SELECT DISTINCT date, team, notes
    FROM temp_schedule_dates_csv
) seed
WHERE sd.date = TO_DATE(seed.date, 'YYYY-MM-DD');

-- truncate the temporary table to prepare for insertions
TRUNCATE TABLE temp_schedule_dates_csv;

-- =============================
-- SPECIAL EVENTS
-- =============================
-- TODO: Run pgAdmin Import to load data from CSV file into the temporary table (insert only)
-- insert special events based on CSV data
INSERT INTO public.schedule_dates (schedule_date_id, schedule_id, date, team_id, schedule_date_type_id, notes, is_active)
SELECT gen_random_uuid(), s.schedule_id, d.date, 
    CASE 
        WHEN seed.team = 'alpha' THEN t_alpha.team_id
        WHEN seed.team = 'omega' THEN t_omega.team_id
        ELSE NULL
    END AS team_id,
    sdt.schedule_date_type_id, seed.notes, true
FROM (
    SELECT DISTINCT date, team, notes
    FROM temp_schedule_dates_csv
) seed
JOIN public.dates d ON d.date = TO_DATE(seed.date, 'YYYY-MM-DD')
JOIN public.schedules s
    ON d.calendar_month = DATE_PART('month', s.month_start_date)
   AND d.calendar_year = DATE_PART('year', s.month_start_date)
JOIN public.schedule_date_types sdt 
    ON sdt.schedule_date_type_code = 'special_event'
JOIN public.teams t_alpha 
    ON t_alpha.team_code = 'alpha'
JOIN public.teams t_omega 
    ON t_omega.team_code = 'omega';

-- update exception Tuesday night midweek service for Thanksgiving week as service, not special event
UPDATE public.schedule_dates sd
SET schedule_date_type_id = sdt.schedule_date_type_id
FROM public.schedule_date_types sdt
WHERE sd.date = '2025-11-25'::date
  AND sdt.schedule_date_type_code = 'service';

-- Drop the temporary table
DROP TABLE IF EXISTS temp_schedule_dates_csv;

-- =============================
-- SCHEDULE DATE ROLES
-- =============================
-- Load CSV data into a temporary table
CREATE TABLE temp_schedule_date_roles_csv (
    date TEXT,
    media_role_code TEXT,
    user_first_name TEXT,
    schedule_type TEXT,
    sound_only TEXT,
    sound_and_propresenter TEXT
);

-- TODO: Run pgAdmin Import to load data from CSV file into the temporary table

-- insert schedule_date_roles based on CSV data
INSERT INTO public.schedule_date_roles (schedule_date_role_id, schedule_date_id, media_role_id, is_required, is_preferred, assigned_user_id, is_active)
SELECT gen_random_uuid(), 
    sd.schedule_date_id,
    mr.media_role_id,
    -- When sound_only is true, only assign sound roles as required (all other roles as not required and not preferred)
    -- When sound_and_propresenter is true, assign both sound and propresenter roles as required (all other roles as not required and not preferred)
    -- Otherwise, assign all roles as required except 'on_call' and 'main_camera_3' (which are not required but preferred)
     CASE 
        WHEN seed.sound_only = 'True' THEN 
            CASE 
                WHEN mr.media_role_code = 'sound' THEN true
                ELSE false
            END
        WHEN seed.sound_and_propresenter = 'True' THEN 
            CASE 
                WHEN mr.media_role_code IN ('sound', 'propresenter') THEN true
                ELSE false
            END
        ELSE
            CASE 
                WHEN mr.media_role_code IN ('on_call', 'main_camera_3') THEN false
                ELSE true
            END
        END AS is_required,
    CASE 
        WHEN seed.sound_only = 'False' AND seed.sound_and_propresenter = 'False' AND mr.media_role_code IN ('on_call', 'main_camera_3') THEN true
        ELSE false
    END AS is_preferred,
    u.user_id AS assigned_user_id,
    true AS is_active
FROM (
    SELECT DISTINCT date, media_role_code, user_first_name, schedule_type, sound_only, sound_and_propresenter
    FROM temp_schedule_date_roles_csv
) AS seed
JOIN public.schedule_date_types sdt 
    ON sdt.schedule_date_type_code = seed.schedule_type
JOIN public.schedule_dates sd 
    ON sd.date = TO_DATE(seed.date, 'YYYY-MM-DD')
    AND sd.schedule_date_type_id = sdt.schedule_date_type_id
JOIN public.media_roles mr 
    ON mr.media_role_code = seed.media_role_code
LEFT JOIN public.users u ON u.first_name = seed.user_first_name;

-- Drop the temporary table
DROP TABLE IF EXISTS temp_schedule_date_roles_csv;

-- =============================
-- USER AVAILABILITY
-- =============================
-- Load CSV data into a temporary table
CREATE TABLE temp_user_availability_csv (
    user_first_name TEXT,
    date TEXT
);

-- TODO: Run pgAdmin Import to load data from CSV file into the temporary table

-- insert user availability based on CSV data
INSERT INTO public.user_availability (user_availability_id, user_id, date)
SELECT gen_random_uuid(), u.user_id, TO_DATE(seed.date, 'YYYY-MM-DD')
FROM (
    SELECT DISTINCT user_first_name, date
    FROM temp_user_availability_csv
) seed
JOIN public.users u ON u.first_name = seed.user_first_name;

-- Drop the temporary table
DROP TABLE IF EXISTS temp_user_availability_csv;