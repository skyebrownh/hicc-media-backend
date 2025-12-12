--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;

--
-- Name: teams; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teams (
    team_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    team_name character varying(50) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    team_code character varying(50) NOT NULL,
    CONSTRAINT teams_ukey UNIQUE (team_code)
);

--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(255),
    phone character varying(50) NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);

--
-- Name: team_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.team_users (
    team_user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id uuid NOT NULL REFERENCES public.teams(team_id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT team_users_ukey UNIQUE (user_id, team_id)
);

--
-- Name: dates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dates (
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
-- Name: media_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.media_roles (
    media_role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    media_role_name character varying(50) NOT NULL,
    description text,
    sort_order smallint NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    media_role_code character varying(50) NOT NULL,
    CONSTRAINT media_roles_ukey UNIQUE (media_role_code)
);

--
-- Name: proficiency_levels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.proficiency_levels (
    proficiency_level_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    proficiency_level_name character varying(50) NOT NULL,
    proficiency_level_number smallint,
    is_active boolean DEFAULT true NOT NULL,
    proficiency_level_code character varying(50) NOT NULL,
    is_assignable boolean DEFAULT false NOT NULL,
    CONSTRAINT proficiency_levels_ukey UNIQUE (proficiency_level_code)
);

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_roles (
    user_role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    media_role_id uuid NOT NULL REFERENCES public.media_roles(media_role_id) ON DELETE CASCADE,
    proficiency_level_id uuid NOT NULL REFERENCES public.proficiency_levels(proficiency_level_id),
    CONSTRAINT user_roles_ukey UNIQUE (user_id, media_role_id)
);

--
-- Name: schedule_date_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_date_types (
    schedule_date_type_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_date_type_name character varying(50) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    schedule_date_type_code character varying(50) NOT NULL,
    CONSTRAINT schedule_date_types_ukey UNIQUE (schedule_date_type_code)
);

--
-- Name: schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedules (
    schedule_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    month_start_date date NOT NULL REFERENCES public.dates(date),
    notes text,
    is_active boolean DEFAULT true NOT NULL
);

--
-- Name: schedule_dates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_dates (
    schedule_date_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id uuid NOT NULL REFERENCES public.schedules(schedule_id) ON DELETE CASCADE,
    date date NOT NULL REFERENCES public.dates(date),
    team_id uuid REFERENCES public.teams(team_id),
    schedule_date_type_id uuid NOT NULL REFERENCES public.schedule_date_types(schedule_date_type_id),
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT schedule_dates_ukey UNIQUE (schedule_id, date, schedule_date_type_id)
);

--
-- Name: schedule_date_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_date_roles (
    schedule_date_role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_date_id uuid NOT NULL REFERENCES public.schedule_dates(schedule_date_id) ON DELETE CASCADE,
    media_role_id uuid NOT NULL REFERENCES public.media_roles(media_role_id),
    is_required boolean DEFAULT true NOT NULL,
    is_preferred boolean DEFAULT false NOT NULL,
    assigned_user_id uuid REFERENCES public.users(user_id),
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT schedule_date_roles_ukey UNIQUE (media_role_id, schedule_date_id, assigned_user_id)
);

--
-- Name: user_availability; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_availability (
    user_availability_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.users(user_id),
    date date NOT NULL REFERENCES public.dates(date),
    CONSTRAINT user_availability_ukey UNIQUE (date, user_id)
);

