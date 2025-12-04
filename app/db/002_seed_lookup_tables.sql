-- =============================
-- MEDIA ROLES
-- =============================
INSERT INTO public.media_roles (media_role_id, media_role_name, sort_order, is_active, media_role_code) VALUES
    (gen_random_uuid(), 'ProPresenter', 10, true, 'propresenter'),
    (gen_random_uuid(), 'Sound', 20, true, 'sound'),
    (gen_random_uuid(), 'Lighting', 30, false, 'lighting'),
    (gen_random_uuid(), 'Camera Director', 40, true, 'camera_director'),
    (gen_random_uuid(), 'Main Camera 1', 50, true, 'main_camera_1'),
    (gen_random_uuid(), 'Main Camera 2', 60, true, 'main_camera_2'),
    (gen_random_uuid(), 'Mobile Camera 3', 70, true, 'mobile_camera_3'),
    (gen_random_uuid(), 'On Call', 80, true, 'on_call');

-- =============================
-- PROFICIENCY LEVELS
-- =============================
INSERT INTO public.proficiency_levels (proficiency_level_id, proficiency_level_name, proficiency_level_number, is_active, proficiency_level_code, is_assignable) VALUES
    (gen_random_uuid(), 'Untrained', 0, true, 'untrained', false),
    (gen_random_uuid(), 'In Training', 1, true, 'in_training', false),
    (gen_random_uuid(), 'Knowledgeable', 2, true, 'knowledgeable', false),
    (gen_random_uuid(), 'Novice', 3, true, 'novice', true),
    (gen_random_uuid(), 'Proficient', 4, true, 'proficient', true),
    (gen_random_uuid(), 'Expert', 5, true, 'expert', true);

-- =============================
-- SCHEDULE DATE TYPES
-- =============================
INSERT INTO public.schedule_date_types (schedule_date_type_id, schedule_date_type_name, is_active, schedule_date_type_code) VALUES
    (gen_random_uuid(), 'Service', true, 'service'),
    (gen_random_uuid(), 'Special Event', true, 'special_event'),
    (gen_random_uuid(), 'Rehearsal', true, 'rehearsal'),
    (gen_random_uuid(), 'Training', true, 'training'),
    (gen_random_uuid(), 'Prayer', true, 'prayer');