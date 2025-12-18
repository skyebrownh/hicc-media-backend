# HICC Media API

FastAPI + Railway Postgres DB + Redis backend for a scheduling application (specifically for a volunteer church media team)

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
    - `test.env`
        - `FAST_API_KEY` - `x-api-key` header is used for auth
4. Run tests (optional)
    ```bash
    pytest
    ```
5. Run dev server
    ```bash
    uv run fastapi dev app/main.py
    ```
    - Server is running on [localhost:8000](http://localhost:8000)
    - Docs are available at [localhost:8000/docs](http://localhost:8000/docs)

## Roadmap

-   [x] Refactor to Railway Postgres DB
-   [x] Refactor FastAPI that runs CRUDs on Railway DB
        routes
-   [x] Refactor unit testing and integration testing with Railway DB
-   [ ] Implement Redis as a cache
-   [ ] Create an auto-scheduling algorithm
