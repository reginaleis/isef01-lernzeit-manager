"""Module specific handling of database operations."""

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.models import Lernziel


class LernzieleDAO:
    """Data access class for Lernziele module."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, lernziel_data: dict) -> Lernziel:
        """Create a new Lernziel in the database."""
        new_lernziel = Lernziel(**lernziel_data)
        self.db.add(new_lernziel)
        await self.db.commit()
        await self.db.refresh(new_lernziel)
        return new_lernziel

    async def get_all(self) -> list[Lernziel]:
        """Retrieve all Lernziele from the database."""
        stmt = select(Lernziel)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, lernziel_id: int) -> Lernziel | None:
        """Retrieve a Lernziel by its ID."""
        stmt = select(Lernziel).where(Lernziel.id == lernziel_id)
        result = await self.db.scalars(stmt)
        return result.one_or_none()

    async def update(self, lernziel_id: int, lernziel_data: dict) -> None:
        """Update an existing Lernziel in the database."""
        stmt = (
            update(Lernziel)
            .where(Lernziel.id == lernziel_id)
            .values(**lernziel_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete(self, lernziel_id: int) -> None:
        """Delete a Lernziel by ID from the database."""
        stmt = delete(Lernziel).where(Lernziel.id == lernziel_id)
        await self.db.execute(stmt)
        await self.db.commit()
