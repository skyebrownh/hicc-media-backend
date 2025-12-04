# HICC Media API

FastAPI + Railway Postgres DB + Redis backend for a scheduling application (specifically for a volunteer church media team)

## Architecture

-   [Fast API](https://fastapi.tiangolo.com/) - Python web framework for the API
-   [Railway](https://railway.com/) - Infrastructure
    -   [Postgres](https://www.postgresql.org/) - Database
    -   [Redis](https://redis.io/) - Cache (coming soon)
-   ~~[Supabase](https://supabase.com/) - Hosted PostgreSQL database~~

## Getting Started / Installation

1. Clone this repo
2. Create and activate Python virtual environment (this project uses v3.13.3)
3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Configure environment variables
    - `.env`
        - ~~`SUPABASE_URL`~~
        - ~~`SUPABASE_API_KEY`~~
        - `FAST_API_KEY` - `x-api-key` header is used for auth
    - `test.env`
        - ~~`SUPABASE_TEST_URL`~~
        - ~~`SUPABASE_TEST_API_KEY`~~
        - `FAST_API_KEY` - `x-api-key` header is used for auth
5. Run tests (optional)
    ```bash
    pytest
    ```
6. Run dev server
    ```bash
    fastapi dev app/main.py
    ```
    - Server is running on [localhost:8000](localhost:8000)
    - Docs are availabile at [localhost:8000/docs](localhost:8000/docs)

## Roadmap

-   [x] ~~Design and launch PostgreSQL database on Supabase~~
-   [x] ~~Create FastAPI that runs CRUDs on Supabase DB~~
-   [x] ~~Implement unit testing and integration testing with Supabase DB~~
-   [x] Refactor to Railway Postgres DB
-   [ ] Refactor FastAPI that runs CRUDs on Railway DB
        routes
-   [ ] Refactor unit testing and integration testing with Railway DB
-   [ ] Implement Redis as a cache
-   [ ] Create an auto-scheduling algorithm
