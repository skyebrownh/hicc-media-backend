# StewardHQ API

StewardHQ is a people-centric platform for managing team scheduling, availability, assignments, and training. This API provides backend services for frontend channels.

## Architecture

-   [Fast API](https://fastapi.tiangolo.com/) - Python web framework for the API
-   [Railway](https://railway.com/) - Infrastructure
    -   [Postgres](https://www.postgresql.org/) - Database
    -   [Redis](https://redis.io/) - Cache (coming soon)

## Getting Started / Installation

1. Clone this repo
2. Create and activate Python virtual environment (v3.13.3) and install dependencies
    ```bash
    uv sync
    ```
3. Configure environment variables
    - `.env`
        - `FAST_API_KEY` - `x-api-key` header is used for auth
        - `RAILWAY_DB_URL` is for remote database connection, and `LOCAL_TEST_DB_URL` is local database connection for tests.
4. Run tests (optional)
    ```bash
    uv run pytest
    ```
5. Run dev server
    ```bash
    uv run fastapi dev app/main.py
    ```
    - Server is running on [localhost:8000](http://localhost:8000)
    - Docs are available at [localhost:8000/docs](http://localhost:8000/docs)

## Roadmap

-   [x] Design the data model and seed historical data
-   [x] Create FastAPI for MVP logic as routes
-   [x] Implement unit and integration testing
-   [ ] Implement Redis as a cache
-   [ ] Create a schedule generation algorithm, including drafting assignments based on rules and constraints
