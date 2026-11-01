"""Database engine configuration."""

import logging
import os
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import event, inspect, text
from sqlalchemy.engine import Connection
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


def migrate_database(connection: Connection) -> None:
    """Apply database migrations before the application serves requests."""
    if connection.dialect.name != "sqlite":
        return

    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            )
            """
        )
    )
    version = connection.execute(text("SELECT MAX(version) FROM schema_version")).scalar_one_or_none() or 0
    if version >= CURRENT_SCHEMA_VERSION:
        return

    inspector = inspect(connection)
    for table_name in ("lernziele", "zwischenziele"):
        if table_name not in inspector.get_table_names():
            continue

        columns = {column["name"] for column in inspector.get_columns(table_name)}
        if "accumulated_study_time" in columns and "accumulated_study_time_min" in columns:
            raise RuntimeError(f"Cannot migrate {table_name}: both accumulated study time columns exist")
        if "accumulated_study_time" in columns:
            connection.execute(
                text(
                    f'ALTER TABLE "{table_name}" RENAME COLUMN "accumulated_study_time" TO "accumulated_study_time_min"'
                )
            )

    connection.execute(text("DELETE FROM schema_version"))
    connection.execute(
        text("INSERT INTO schema_version (version) VALUES (:version)"),
        {"version": CURRENT_SCHEMA_VERSION},
    )
    logger.info("Database migrated to schema version %s", CURRENT_SCHEMA_VERSION)


class Base(DeclarativeBase):
    """Base class for typed SQLAlchemy models."""


async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide one database session per request."""
    logger.debug("Opening database session")
    async with session_factory() as session:
        yield session
    logger.debug("Closed database session")
