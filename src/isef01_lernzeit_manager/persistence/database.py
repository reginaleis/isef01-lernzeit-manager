"""Database engine configuration."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./isef01.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for typed SQLAlchemy models."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Abstract database session provider for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
