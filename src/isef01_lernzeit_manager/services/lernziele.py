"""Backend service for Lernziele."""

from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.data_access import LernzieleDAO
from isef01_lernzeit_manager.persistence.models import Lernziel


class LernzieleService:
    def __init__(self, db_session: AsyncSession):
        self.dao = LernzieleDAO(db_session)

    async def get_all_lernziele(self) -> list[Lernziel]:
        """Alle Lernziele abrufen."""
        return await self.dao.get_all()

    async def create_lernziel(self, lernziel_data: dict[str, object]) -> Lernziel:
        """Neues Lernziel anlegen."""
        return await self.dao.create(lernziel_data)
