from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import asyncpg
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """
    Register exception handlers for the FastAPI application.
    
    This function sets up handlers for various exception types to ensure
    consistent error responses and proper logging without exposing internal
    implementation details to clients.
    
    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle HTTPException raised by the application.
        
        These are intentional exceptions (e.g., 404, 401) that should be
        returned to the client as-is.
        """
        logger.warning(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle request validation errors from Pydantic.
        
        Returns validation errors to help clients fix their request format.
        """
        logger.warning(f"RequestValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body},
        )

    @app.exception_handler(asyncpg.PostgresError)
    async def postgres_exception_handler(request: Request, exc: asyncpg.PostgresError):
        """
        Handle PostgreSQL database errors.
        
        Logs the full error internally but returns a generic message to clients
        to avoid exposing database structure or internal details.
        """
        logger.error(f"PostgresError: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Database operation failed"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle all other unhandled exceptions.
        
        Logs the full exception with stack trace internally but returns a
        generic error message to clients to avoid exposing implementation details.
        """
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred"},
        )