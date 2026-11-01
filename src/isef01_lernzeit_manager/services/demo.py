"""Application service for restoring demo data."""

import json
import logging
from pathlib import Path
from typing import Any, cast

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.tables import Lernzeiten, Lernziel, Module, Zwischenziel

DEMO_DATA_FILE = Path(__file__).parent.parent / "persistence" / "demo_data.json"
logger = logging.getLogger(__name__)


class DemoService:
    """Service for resetting the database to its predefined demo state."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def reset_data(self) -> None:
        """Alle gespeicherten Daten löschen und mit Demo-Daten überschreiben."""
        logger.info("Resetting database with demo data")
        demo_data = self._load_demo_data()

        async with self.session.begin():
            await self.session.execute(delete(Lernzeiten))
            await self.session.execute(delete(Zwischenziel))
            await self.session.execute(delete(Lernziel))
            await self.session.execute(delete(Module))

            modules = [Module(**record) for record in demo_data["modules"]]
            self.session.add_all(modules)
            await self.session.flush()

            lernziele = [Lernziel(**record) for record in demo_data["lernziele"]]
            self.session.add_all(lernziele)
            await self.session.flush()

            zwischenziele = [Zwischenziel(**record) for record in demo_data["zwischenziele"]]
            self.session.add_all(zwischenziele)
            await self.session.flush()

            self.session.add_all(Lernzeiten(**record) for record in demo_data["lernzeiten"])
        logger.info("Database reset with demo data")

    @staticmethod
    def _load_demo_data() -> dict[str, list[dict[str, Any]]]:
        """Demo Daten aus JSON-Datei laden."""
        with DEMO_DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Demo data must be a JSON object.")
        return cast(dict[str, list[dict[str, Any]]], data)
