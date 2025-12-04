-- =============================
-- USERS
-- =============================
INSERT INTO public.users (user_id, first_name, last_name, email, phone, is_active) VALUES 
    (gen_random_uuid(), 'Johnathan', 'Vaughn', null, '2026413546', 'true'), 
    (gen_random_uuid(), 'Antoinette', 'Pitts', null, '2702685127', 'true'), 
    (gen_random_uuid(), 'Jaime', 'Boyd', null, '2702722896', 'true'), 
    (gen_random_uuid(), 'Michael', 'Hudson', 'mhud32@gmail.com', '2708728388', 'true'), 
    (gen_random_uuid(), 'William', 'Gilmore', null, '2705055383', 'true'), 
    (gen_random_uuid(), 'Skye', 'Brown', 'skye.brownh@gmail.com', '2703008405', 'true'), 
    (gen_random_uuid(), 'Horace', 'Dillard', null, '2703196555', 'true'), 
    (gen_random_uuid(), 'Andrew', 'Roach', null, '5126399960', 'false'), 
    (gen_random_uuid(), 'Gary', 'Elias Sr', null, '2703175566', 'true'), 
    (gen_random_uuid(), 'Vivian', 'Robinson', null, '9312188779', 'true'), 
    (gen_random_uuid(), 'Frank', 'Anderson', null, '2702689679', 'true'), 
    (gen_random_uuid(), 'Marcus', 'Pitts', 'marcuspitts25@gmail.com', '2705067988', 'true'), 
    (gen_random_uuid(), 'Mario', 'Hodge', null, '2703006425', 'true'), 
    (gen_random_uuid(), 'Alexis', 'Williams', null, '5023782871', 'true'),
    (gen_random_uuid(), 'Harry', 'Parent', null, '2703178092', 'true'),
    (gen_random_uuid(), 'Jarrell', 'Russell', null, '2703199324', 'true');

-- =============================
-- TEAMS
-- =============================
INSERT INTO public.teams (team_id, team_name, is_active, team_code) VALUES
    (gen_random_uuid(), 'Alpha', true, 'alpha'),
    (gen_random_uuid(), 'Omega', true, 'omega');

-- =============================
-- TEAM USERS
-- =============================
INSERT INTO team_users(team_user_id, team_id, user_id, is_active)
SELECT gen_random_uuid(), t.team_id, u.user_id, true
FROM public.teams t
CROSS JOIN public.users u
WHERE (t.team_code = 'alpha' AND u.first_name IN ('Michael', 'William', 'Gary', 'Skye', 'Vivian', 'Horace', 'Alexis', 'Harry'))
   OR (t.team_code = 'omega' AND u.first_name IN ('Marcus', 'Mario', 'Jaime', 'Frank', 'Johnathan', 'Andrew', 'Jarrell'));

-- =============================
-- USER ROLES
-- =============================
-- Load CSV data into a temporary table
CREATE TABLE temp_user_roles_csv (
    user_first_name TEXT,
    media_role_name TEXT,
    proficiency_level_number INT
);

-- TODO: Run pgAdmin Import to load data from CSV file into the temporary table

-- insert user roles based on CSV data
INSERT INTO public.user_roles (user_role_id, user_id, media_role_id, proficiency_level_id)
SELECT gen_random_uuid(), u.user_id, m.media_role_id, p.proficiency_level_id
FROM (
    SELECT DISTINCT user_first_name, media_role_name, proficiency_level_number
    FROM temp_user_roles_csv
) seed
JOIN public.users u ON u.first_name = seed.user_first_name
JOIN public.media_roles m ON m.media_role_name = seed.media_role_name
JOIN public.proficiency_levels p ON p.proficiency_level_number = seed.proficiency_level_number;

-- Drop the temporary table
DROP TABLE IF EXISTS temp_user_roles_csv;