"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine

from app.core.config import settings

# Create synchronous engine for migrations and simple operations
# Use asyncpg for async operations, sqlite for testing/sync operations
sync_url = str(settings.SQLALCHEMY_DATABASE_URI)
if "+asyncpg" in sync_url:
    # For production/development with PostgreSQL
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
else:
    # Fallback URL
    sync_url = "sqlite:///./test.db"

engine = create_engine(sync_url, echo=settings.ENVIRONMENT == "development")

# Create async engine for main application
async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=settings.ENVIRONMENT == "development")

# Session makers
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


def get_db():
    """
    Get database session for dependency injection.

    Yields:
        Session: SQLModel database session
    """
    with SessionLocal() as session:
        try:
            yield session
        finally:
            session.close()


async def get_async_db():
    """
    Get async database session for dependency injection.

    Yields:
        AsyncSession: Async SQLModel database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
