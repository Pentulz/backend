import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import database
from app.api.v1 import health

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
app.include_router(health.router, prefix="/api/v1", tags=["Health"])


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.app_name,
        "environment": settings.environment,
        "version": "0.1.0",
        "docs": "/docs",
    }
