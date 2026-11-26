"""Application service for restoring demo data."""

import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, cast

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.tables import Lernzeiten, Lernziel, Zwischenziel

DEMO_DATA_FILE = Path(__file__).parent.parent / "persistence" / "demo_data.json"
DEMO_FALLBACK_DATE = date(2026, 12, 24)
logger = logging.getLogger(__name__)


class DemoService:
    """Service for resetting the database to its predefined demo state."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def reset_data(self) -> None:
        """Alle gespeicherten Daten löschen und mit Demo-Daten überschreiben."""
        logger.debug("Resetting database with demo data")
        demo_data = self._load_demo_data()

        async with self.session.begin():
            await self.session.execute(delete(Lernzeiten))
            await self.session.execute(delete(Zwischenziel))
            await self.session.execute(delete(Lernziel))

            lernziele = [Lernziel(**record) for record in demo_data["lernziele"]]
            self.session.add_all(lernziele)
            await self.session.flush()

            zwischenziele = [Zwischenziel(**record) for record in demo_data["zwischenziele"]]
            self.session.add_all(zwischenziele)
            await self.session.flush()

            self.session.add_all(Lernzeiten(**record) for record in demo_data["lernzeiten"])
        logger.debug("Database reset with demo data")

    @staticmethod
    def _load_demo_data() -> dict[str, list[dict[str, Any]]]:
        """Demo Daten aus JSON-Datei laden."""
        try:
            with DEMO_DATA_FILE.open(encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Demo data must be a JSON object.")
            return cast(dict[str, list[dict[str, Any]]], DemoService._shift_dates(data))
        except (OSError, json.JSONDecodeError, ValueError, TypeError, OverflowError) as err:
            with DEMO_DATA_FILE.open(encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Demo fallback data must be a JSON object.") from err
            return cast(dict[str, list[dict[str, Any]]], data)

    @staticmethod
    def _shift_dates(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        """Dates in the JSON fallback are based on 24.12.2026."""
        delta = date.today() - DEMO_FALLBACK_DATE

        def shift(value: Any) -> Any:
            if isinstance(value, dict):
                return {key: shift(item) for key, item in value.items()}
            if isinstance(value, list):
                return [shift(item) for item in value]
            if not isinstance(value, str):
                return value
            if len(value) == 10:
                try:
                    return (date.fromisoformat(value) + delta).isoformat()
                except ValueError:
                    return value
            if "T" in value:
                try:
                    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    return (parsed + delta).isoformat().replace("+00:00", "Z")
                except ValueError:
                    return value
            return value

        return cast(dict[str, list[dict[str, Any]]], shift(data))
