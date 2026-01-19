# API Routes

## Roles
- `GET /roles` - Get all roles
- `GET /roles/{id}` - Get single role
- `POST /roles` - Create role (subsequently creates user_roles for all users)
- `PATCH /roles/{id}` - Update role
- `DELETE /roles/{id}` - Delete role

## Proficiency Levels
- `GET /proficiency_levels` - Get all proficiency levels
- `GET /proficiency_levels/{id}` - Get single proficiency level
- `POST /proficiency_levels` - Create proficiency level
- `PATCH /proficiency_levels/{id}` - Update proficiency level
- `DELETE /proficiency_levels/{id}` - Delete proficiency level

## Event Types
- `GET /event_types` - Get all event types
- `GET /event_types/{id}` - Get single event type
- `POST /event_types` - Create event type
- `PATCH /event_types/{id}` - Update event type
- `DELETE /event_types/{id}` - Delete event type

## Teams
- `GET /teams` - Get all teams
- `GET /teams/{id}` - Get single team
- `POST /teams` - Create team
- `PATCH /teams/{id}` - Update team
- `DELETE /teams/{id}` - Delete team

## Users
- `GET /users` - Get all users
- `GET /users/{id}` - Get single user
- `POST /users` - Create user (subsequently create user_roles for all roles)
- `PATCH /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

## Team Users
- `GET /teams/{team_id}/users` - Get team users for team
- `POST /teams/{team_id}/users` - Create team user for team
- `PATCH /teams/{team_id}/users/{user_id}` - Update team user
- `DELETE /teams/{team_id}/users/{user_id}` - Delete team user

There is no GET single endpoint since the projected volume is not high enough for it to be relevant.

## User Roles
- `GET /users/{user_id}/roles` - Get roles for user
- `GET /roles/{role_id}/users` - Get users for role
- `PATCH /users/{user_id}/roles/{role_id}` - Update user role

There is no GET single endpoint since the projected volume is not high enough for it to be relevant.

User roles are not created or deleted directly through API endpoints. A cross of all users and roles should always be present, so this is managed from those parent resources.

## Schedules
- `GET /schedules` - Get all schedules
- `GET /schedules/{id}` - Get single schedule
- `GET /schedules/{id}/grid` - Get schedule grid (includes events, assignments, and availability)
- `POST /schedules` - Create schedule
- `PATCH /schedules/{id}` - Update schedule
- `DELETE /schedules/{id}` - Delete schedule

## Events
- `GET /schedules/{schedule_id}/events` - Get events for schedule (includes assignments)
- `GET /events/{id}` - Get single event (includes assignments)
- `POST /schedules/{schedule_id}/events` - Create event for schedule (with default assignments as all active roles with all applicable and required)
- `PATCH /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event

## Event Assignments
- `GET /events/{event_id}/assignments` - Get assignments by event
- `PATCH /assignments/{id}` - Update event assignment

There is no GET single endpoint since assignments are relevant within their parent event and will be queried together.

Event assignments are not created or deleted directly through API endpoints. They are inserted when a new event is created and cascade deleted when an event is deleted.

## User Unavailable Periods
- `POST /users/{user_id}/availability` - Create user unavailable period
- `POST /users/{user_id}/availability/bulk` - Create user unavailable periods in bulk
- `PATCH /user_availability/{id}` - Update user unavailable period
- `DELETE /user_availability/{id}` - Delete user unavailable period

There are no GET endpoints since availability is returned through querying schedules and events.