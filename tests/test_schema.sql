DROP SCHEMA IF EXISTS test_schema CASCADE;
CREATE SCHEMA test_schema;
SET search_path TO test_schema;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA test_schema;

--
-- Name: teams; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.teams (
    team_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    team_name character varying(50) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    team_code character varying(50) NOT NULL
);

--
-- Name: users; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.users (
    user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(255),
    phone character varying(50) NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);

--
-- Name: team_users; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.team_users (
    team_user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id uuid NOT NULL REFERENCES test_schema.teams(team_id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES test_schema.users(user_id) ON DELETE CASCADE,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT team_users_ukey UNIQUE (user_id, team_id)
);

--
-- Name: dates; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.dates (
    date date PRIMARY KEY,
    calendar_year smallint,
    calendar_month smallint,
    month_name character varying(30),
    month_abbr character(3),
    calendar_day smallint,
    weekday smallint,
    weekday_name character varying(30),
    is_weekend boolean DEFAULT false NOT NULL,
    is_weekday boolean DEFAULT false NOT NULL,
    is_holiday boolean DEFAULT false NOT NULL,
    week_number smallint,
    is_first_of_month boolean DEFAULT false NOT NULL,
    is_last_of_month boolean DEFAULT false NOT NULL,
    calendar_quarter smallint,
    weekday_of_month smallint
);

--
-- Name: media_roles; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.media_roles (
    media_role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    media_role_name character varying(50) NOT NULL,
    description text,
    sort_order smallint NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    media_role_code character varying(50) NOT NULL
);

--
-- Name: proficiency_levels; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.proficiency_levels (
    proficiency_level_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    proficiency_level_name character varying(50) NOT NULL,
    proficiency_level_number smallint,
    is_active boolean DEFAULT true NOT NULL,
    proficiency_level_code character varying(50) NOT NULL,
    is_assignable boolean DEFAULT false NOT NULL
);

--
-- Name: user_roles; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.user_roles (
    user_role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES test_schema.users(user_id) ON DELETE CASCADE,
    media_role_id uuid NOT NULL REFERENCES test_schema.media_roles(media_role_id) ON DELETE CASCADE,
    proficiency_level_id uuid NOT NULL REFERENCES test_schema.proficiency_levels(proficiency_level_id),
    CONSTRAINT user_roles_ukey UNIQUE (user_id, media_role_id)
);

--
-- Name: schedule_date_types; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.schedule_date_types (
    schedule_date_type_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_date_type_name character varying(50) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    schedule_date_type_code character varying(50) NOT NULL
);

--
-- Name: schedules; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.schedules (
    schedule_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    month_start_date date NOT NULL REFERENCES test_schema.dates(date),
    notes text,
    is_active boolean DEFAULT true NOT NULL
);

--
-- Name: schedule_dates; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.schedule_dates (
    schedule_date_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id uuid NOT NULL REFERENCES test_schema.schedules(schedule_id) ON DELETE CASCADE,
    date date NOT NULL REFERENCES test_schema.dates(date),
    team_id uuid REFERENCES test_schema.teams(team_id),
    schedule_date_type_id uuid NOT NULL REFERENCES test_schema.schedule_date_types(schedule_date_type_id),
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT schedule_dates_ukey UNIQUE (schedule_id, date, schedule_date_type_id)
);

--
-- Name: schedule_date_roles; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.schedule_date_roles (
    schedule_date_role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_date_id uuid NOT NULL REFERENCES test_schema.schedule_dates(schedule_date_id) ON DELETE CASCADE,
    media_role_id uuid NOT NULL REFERENCES test_schema.media_roles(media_role_id),
    is_required boolean DEFAULT true NOT NULL,
    is_preferred boolean DEFAULT false NOT NULL,
    assigned_user_id uuid REFERENCES test_schema.users(user_id),
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT schedule_date_roles_ukey UNIQUE (media_role_id, schedule_date_id, assigned_user_id)
);

--
-- Name: user_availability; Type: TABLE; Schema: test_schema; Owner: -
--

CREATE TABLE test_schema.user_availability (
    user_availability_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES test_schema.users(user_id),
    date date NOT NULL REFERENCES test_schema.dates(date),
    CONSTRAINT user_availability_ukey UNIQUE (date, user_id)
);