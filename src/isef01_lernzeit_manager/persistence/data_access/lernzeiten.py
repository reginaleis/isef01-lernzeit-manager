"""Lernzeiten Data Access Layer."""

import logging
from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.exceptions import LernzielNotFoundError, ZwischenzielNotFoundError
from isef01_lernzeit_manager.persistence.tables import Lernzeiten, Lernziel, Zwischenziel

logger = logging.getLogger(__name__)


class LernzeitenDAO:
    """Data access class for Lernzeiten module."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, lernzeit_data: Mapping[str, object]) -> Lernzeiten:
        """Neue Lernzeit in Datenbank speichern."""
        logger.debug("Persisting new Lernzeit")
        new_lernzeit = Lernzeiten(**dict(lernzeit_data))
        self.db.add(new_lernzeit)
        await self.db.commit()
        await self.db.refresh(new_lernzeit)
        return new_lernzeit

    async def get_all(self) -> list[Lernzeiten]:
        """Alle Lernzeiten aus der Datenbank abrufen."""
        logger.debug("Loading all Lernzeiten")
        stmt = select(Lernzeiten)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, lernzeit_id: int) -> Lernzeiten | None:
        """Lernzeit anhand ihrer ID abrufen."""
        stmt = select(Lernzeiten).where(Lernzeiten.id == lernzeit_id)
        result = await self.db.scalars(stmt)
        return result.one_or_none()

    async def update(self, lernzeit_id: int, lernzeit_data: Mapping[str, object]) -> Lernzeiten | None:
        """Vorhandene Lernzeit in der Datenbank aktualisieren."""
        lernzeit = await self.get_by_id(lernzeit_id)
        if lernzeit is None:
            return None
        for field, value in lernzeit_data.items():
            setattr(lernzeit, field, value)
        await self.db.commit()
        await self.db.refresh(lernzeit)
        return lernzeit

    async def delete(self, lernzeit_id: int) -> Lernzeiten | None:
        """Lernzeit aus der Datenbank löschen."""
        lernzeit = await self.get_by_id(lernzeit_id)
        if lernzeit is None:
            return None
        await self.db.delete(lernzeit)
        await self.db.commit()
        return lernzeit

    async def get_filtered_lernzeiten(self, filters: Mapping[str, object]) -> list[Lernzeiten]:
        """Lernzeiten anhand von Filtern abrufen."""
        logger.debug("Loading filtered Lernzeiten")
        stmt = select(Lernzeiten)
        for field, value in filters.items():
            stmt = stmt.where(getattr(Lernzeiten, field) == value)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def ensure_lernziel_exists(self, lernziel_id: int | None) -> None:
        """Raise a user-friendly error if the referenced Lernziel does not exist."""
        if lernziel_id is None:
            return
        stmt = select(Lernziel.id).where(Lernziel.id == lernziel_id)
        if await self.db.scalar(stmt) is None:
            raise LernzielNotFoundError(lernziel_id)

    async def ensure_zwischenziel_exists(self, zwischenziel_id: int | None) -> None:
        """Raise a user-friendly error if the referenced Zwischenziel does not exist."""
        if zwischenziel_id is None:
            return
        stmt = select(Zwischenziel.id).where(Zwischenziel.id == zwischenziel_id)
        if await self.db.scalar(stmt) is None:
            raise ZwischenzielNotFoundError(zwischenziel_id)
