
"""Gemeinsame Konfiguration für pytest."""

import asyncio
import os
from pathlib import Path

import pytest

# Testdatenbank vor dem Import der Anwendung festlegen
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DB = PROJECT_ROOT / ".venv" / "test_isef01.db"

os.environ["DATABASE_URL"] = str(TEST_DB)

from isef01_lernzeit_manager.main import app  # noqa: E402
from isef01_lernzeit_manager.persistence.database import (  # noqa: E402
    Base,
    engine,
)


async def reset_test_database():
    """Tabellen der Testdatenbank zurücksetzen."""

    # Sicherheitsprüfung: Niemals die normale Datenbank löschen
    actual_db = Path(engine.url.database).resolve()
    assert actual_db == TEST_DB.resolve(), (
        "Abbruch: Es wurde nicht die Testdatenbank erkannt!"
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def clean_database():
    """Vor jedem Test eine saubere Datenbank bereitstellen."""
    asyncio.run(reset_test_database())
