"""Zwischenziele Data Access Object"""

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.exceptions import LernzielNotFoundError
from isef01_lernzeit_manager.persistence.tables import Lernzeiten, Lernziel, Zwischenziel


class ZwischenzieleDAO:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, zwischenziel_data: dict) -> "Zwischenziel":
        """Neues Zwischenziel in der Datenbank speichern."""
        await self.ensure_lernziel_exists(zwischenziel_data["lernziel_id"])
        new_zwischenziel = Zwischenziel(**zwischenziel_data)
        self.db.add(new_zwischenziel)
        await self.db.commit()
        await self.db.refresh(new_zwischenziel)
        return new_zwischenziel

    async def get_all(self) -> list["Zwischenziel"]:
        """Alle Zwischenziele aus der Datenbank abrufen."""
        stmt = select(Zwischenziel)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def update(self, zwischenziel_id: int, zwischenziel_data: dict) -> "Zwischenziel" | None:
        """Vorhandenes Zwischenziel in der Datenbank aktualisieren."""
        zwischenziel = await self.get_by_id(zwischenziel_id)
        if zwischenziel is None:
            return None
        await self.ensure_lernziel_exists(zwischenziel_data.get("lernziel_id", zwischenziel.lernziel_id))
        for field, value in zwischenziel_data.items():
            setattr(zwischenziel, field, value)
        await self.db.commit()
        await self.db.refresh(zwischenziel)
        return zwischenziel

    async def delete(self, zwischenziel_id: int) -> "Zwischenziel" | None:
        """Zwischenziel aus der Datenbank löschen."""
        zwischenziel = await self.get_by_id(zwischenziel_id)
        if zwischenziel is None:
            return None
        await self.db.delete(zwischenziel)
        await self.db.commit()
        return zwischenziel

    async def has_dependents(self, zwischenziel_id: int) -> bool | None:
        """Check, ob ein Zwischenziel referenziert wird."""
        stmt = select(exists().where(Lernzeiten.zwischenziel_id == zwischenziel_id))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_by_id(self, zwischenziel_id: int) -> "Zwischenziel" | None:
        """Zwischenziel anhand der ID abrufen."""
        stmt = select(Zwischenziel).where(Zwischenziel.id == zwischenziel_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_lernziel_id(self, lernziel_id: int) -> list["Zwischenziel"]:
        """Alle Zwischenziele für ein bestimmtes Lernziel abrufen."""
        stmt = select(Zwischenziel).where(Zwischenziel.lernziel_id == lernziel_id)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def ensure_lernziel_exists(self, lernziel_id: int | str | None) -> None:
        """Raise a user-friendly error if the referenced Lernziel does not exist."""
        stmt = select(Lernziel.id).where(Lernziel.id == lernziel_id)
        if await self.db.scalar(stmt) is None:
            raise LernzielNotFoundError(lernziel_id)
