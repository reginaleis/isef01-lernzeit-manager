"""Backend service for Lernziele."""

import logging
from collections.abc import Mapping

from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.data_access import LernzieleDAO
from isef01_lernzeit_manager.persistence.tables import Lernziel
from isef01_lernzeit_manager.pydantic_models import LernzieleCreate

logger = logging.getLogger(__name__)


class LernzieleService:
    def __init__(self, db_session: AsyncSession):
        self.dao = LernzieleDAO(db_session)

    async def get_all_lernziele(self) -> list[Lernziel]:
        """Alle Lernziele abrufen."""
        logger.info("Fetching all Lernziele")
        return await self.dao.get_all()

    async def create_lernziel(
        self,
        lernziel_data: LernzieleCreate | Mapping[str, object],
    ) -> Lernziel:
        """Validate and persist a new Lernziel."""
        logger.info("Creating Lernziel")
        lernziel = LernzieleCreate.model_validate(lernziel_data)
        return await self.dao.create(lernziel.model_dump(mode="json"))
