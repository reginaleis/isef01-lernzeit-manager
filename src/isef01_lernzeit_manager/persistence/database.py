"""Database engine configuration."""

import logging
import os
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./isef01.db")

logger = logging.getLogger(__name__)

engine = create_async_engine(DATABASE_URL, echo=False)
session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
CURRENT_SCHEMA_VERSION = 1


@event.listens_for(engine.sync_engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
    """Enable foreign-key enforcement for each SQLite connection."""
    if engine.dialect.name != "sqlite":
        return

    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


class Base(DeclarativeBase):
    """Base class for typed SQLAlchemy models."""


async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide one database session per request."""
    logger.debug("Opening database session")
    async with session_factory() as session:
        yield session
    logger.debug("Closed database session")
