import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

from .config import Settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine: AsyncEngine | None = None
        self.async_session_local: sessionmaker | None = None

    def connect(self):
        """Initialize database connection"""
        try:
            database_url = self.settings.get_database_url()

            self.engine = create_async_engine(
                database_url,
                echo=self.settings.debug,  # Log SQL queries in debug mode
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300,  # Recycle connections every 5 min
            )

            self.async_session_local = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,  # Manual flush control
                autocommit=False,
            )

            logger.info(
                f"Database connected: {self.settings.DATABASE_HOST}:{self.settings.DATABASE_PORT}"
            )

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    async def disconnect(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database disconnected")

    async def create_tables(self):
        """Create all tables (for development)"""
        if self.engine:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")


# Global database instance
database = Database(get_settings())


# Dependency for FastAPI routes
async def get_db() -> AsyncSession:
    """FastAPI dependency to get database session"""
    if not database.async_session_local:
        raise RuntimeError("Database not connected. Call database.connect() first.")

    async with database.async_session_local() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
