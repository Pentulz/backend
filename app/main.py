import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import agents, health, jobs, reports, system
from app.core.config import get_settings
from app.core.database import database
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, Depends, Request

# Configure logging
logging.basicConfig(
    level=getattr(logging, "INFO"),
    # If we want to include the logger name in the output :
    # format='%(levelname)-9s %(name)-20s %(message)s'
    format="%(levelname)-9s %(message)s",
)

# Disable SQLAlchemy logging completely
logging.getLogger("sqlalchemy.engine.Engine").disabled = True

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup events
    logger.info("Starting %s in %s mode", settings.name, settings.environment)

    # Connect to database
    database.connect()
    logger.info("Database connection established")

    # Create tables in development mode
    if settings.environment == "dev":
        await database.create_tables()
        logger.info("Database tables created/verified")

    yield

    # Shutdown events
    logger.info("Shutting down application")
    await database.disconnect()
    logger.info("Database connection closed")


app = FastAPI(
    title=settings.name,
    debug=settings.debug,
    lifespan=lifespan,
    description="Pentulz - Penetration Testing Orchestration Platform",
    version="0.1.0",
)

# Include routers
app.include_router(system.router, prefix=settings.API_PREFIX, tags=["System"])
app.include_router(health.router, prefix=settings.API_PREFIX, tags=["Health"])
app.include_router(jobs.router, prefix=settings.API_PREFIX, tags=["Jobs"])
app.include_router(reports.router, prefix=settings.API_PREFIX, tags=["Reports"])
app.include_router(agents.router, prefix=settings.API_PREFIX, tags=["Agents"])

import json


async def generic_error_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler that returns errors in the same JSON format
    """
    # Default status
    status_code = 500
    title = "Internal Server Error"

    # If it's a Pydantic validation error, override
    if isinstance(exc, RequestValidationError):
        status_code = 422
        title = "Validation Error"
        errors = []
        for e in exc.errors():
            loc_str = " -> ".join(str(x) for x in e.get("loc", []))
            errors.append(
                {
                    "status": str(status_code),
                    "title": title,
                    "detail": f"{loc_str}: {e.get('msg', 'Invalid input')}",
                }
            )
    else:
        errors = [{"status": str(status_code), "title": title, "detail": str(exc)}]

    return JSONResponse(status_code=status_code, content={"errors": errors})


# Register handler for all exceptions
app.add_exception_handler(Exception, generic_error_handler)
app.add_exception_handler(RequestValidationError, generic_error_handler)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.name,
        "environment": settings.environment,
        "version": "0.1.0",
        "docs": "/docs",
    }
