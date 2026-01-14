# StewardHQ API

StewardHQ is a people-centric platform for managing team scheduling, availability, assignments, and training. This repository contains the backend API that powers StewardHQ's frontend applications.

## Architecture

-   [Fast API](https://fastapi.tiangolo.com/) - Python web framework
-   [Railway](https://railway.com/) - Hosting an infrastructure
    -   [Postgres](https://www.postgresql.org/) - Database
    -   [Redis](https://redis.io/) - Cache (coming soon)

## Getting Started / Installation

1. Clone this repo
2. Create and activate Python virtual environment (Python 3.13.3 recommended), then install dependencies:
    ```bash
    uv sync
    ```
3. Configure environment variables
    - `.env`
        - `FAST_API_KEY` – API key used for `x-api-key` header authentication
        - `RAILWAY_DB_URL` – Remote database connection string
        - `LOCAL_TEST_DB_URL` – Local database connection string used for tests
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
-   [x] Implement FastAPI routes for MVP business logic
-   [x] Implement unit and integration testing
-   [ ] Implement Redis as a cache
-   [ ] Implement a schedule generation engine with rule- and constraint-based assignment logic
