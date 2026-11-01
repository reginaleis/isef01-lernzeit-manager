"""Module specific handling of database operations."""

import logging
from collections.abc import Mapping
from datetime import date

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.tables import Lernzeiten, Lernziel, Zwischenziel

logger = logging.getLogger(__name__)


class LernzieleDAO:
    """Data access class for Lernziele module."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, lernziel_data: Mapping[str, object]) -> Lernziel:
        """Neues Ziel in Datenbank speichern."""
        logger.info("Persisting new Lernziel")
        new_lernziel = Lernziel(**dict(lernziel_data))
        self.db.add(new_lernziel)
        await self.db.commit()
        await self.db.refresh(new_lernziel)
        return new_lernziel

    async def get_all(self) -> list[Lernziel]:
        """Alle Lernziele aus der Datenbank abrufen."""
        logger.info("Loading all Lernziele")
        stmt = select(Lernziel)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def update(self, lernziel_id: int, lernziel_data: Mapping[str, object]) -> Lernziel | None:
        """Vorhandenes Lernziel in der Datenbank aktualisieren."""
        lernziel = await self.get_by_id(lernziel_id)
        if lernziel is None:
            return None
        for field, value in lernziel_data.items():
            setattr(lernziel, field, value)
        await self.db.commit()
        await self.db.refresh(lernziel)
        return lernziel

    async def delete(self, lernziel_id: int) -> Lernziel | None:
        """Lernziel aus der Datenbank löschen."""
        lernziel = await self.get_by_id(lernziel_id)
        if lernziel is None:
            return None
        await self.db.delete(lernziel)
        await self.db.commit()
        return lernziel

    async def has_dependents(self, lernziel_id: int) -> bool:
        """Check whether a Lernziel is referenced by child records."""
        stmt = select(
            exists().where(Zwischenziel.lernziel_id == lernziel_id),
            exists().where(Lernzeiten.lernziel_id == lernziel_id),
        )
        has_zwischenziele, has_lernzeiten = (await self.db.execute(stmt)).one()
        return has_zwischenziele or has_lernzeiten

    async def get_by_id(self, lernziel_id: int) -> Lernziel | None:
        """Lernziel anhand der ID abrufen."""
        stmt = select(Lernziel).where(Lernziel.id == lernziel_id)
        result = await self.db.scalars(stmt)
        return result.one_or_none()

    async def get_lernziele_in_range(self, from_date: date, to_date: date) -> list[Lernziel]:
        """Lernziele in einem bestimmten Datumsbereich abrufen."""
        from_date_value = from_date.isoformat()
        to_date_value = to_date.isoformat()
        logger.info(f"Fetching Lernziele where start_date is between {from_date_value} and {to_date_value}")
        stmt = select(Lernziel).where(
            Lernziel.start_date >= from_date_value,
            Lernziel.start_date <= to_date_value,
        )
        result = await self.db.scalars(stmt)
        return list(result.all())
