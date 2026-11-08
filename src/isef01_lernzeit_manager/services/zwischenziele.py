"""Service Zwischenziele."""

import logging
from collections.abc import Mapping

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.exceptions import (
    ZwischenzielHasDependentsError,
    ZwischenzielNotFoundError,
)
from isef01_lernzeit_manager.persistence.data_access import ZwischenzieleDAO
from isef01_lernzeit_manager.persistence.database import get_session
from isef01_lernzeit_manager.persistence.tables import Zwischenziel
from isef01_lernzeit_manager.pydantic_models import ZwischenzielCreate, ZwischenzielUpdate

logger = logging.getLogger(__name__)


class ZwischenzieleService:
    def __init__(self, db_session: AsyncSession):
        self.dao = ZwischenzieleDAO(db_session)

    async def get_all_zwischenziele(self) -> list[Zwischenziel]:
        """Alle Zwischenziele abrufen."""
        logger.debug("Fetching all Zwischenziele")
        return await self.dao.get_all()

    async def create_zwischenziel(
        self,
        zwischenziel_data: ZwischenzielCreate | Mapping[str, object],
    ) -> Zwischenziel:
        """Validate and persist a new Zwischenziel."""
        logger.debug("Creating Zwischenziel")
        zwischenziel = ZwischenzielCreate.model_validate(zwischenziel_data)
        data = zwischenziel.model_dump(mode="json")
        await self.dao.ensure_lernziel_exists(data["lernziel_id"])
        return await self.dao.create(data)

    async def get_zwischenziel(self, zwischenziel_id: int) -> Zwischenziel:
        """Retrieve a Zwischenziel by its ID."""
        logger.debug(f"Fetching Zwischenziel with ID: {zwischenziel_id}")
        zwischenziel = await self.dao.get_by_id(zwischenziel_id)
        if zwischenziel is None:
            raise ZwischenzielNotFoundError(zwischenziel_id)
        return zwischenziel

    async def update_zwischenziel(
        self,
        zwischenziel_id: int,
        zwischenziel_data: ZwischenzielUpdate | Mapping[str, object],
    ) -> Zwischenziel | None:
        """Validate and update an existing Zwischenziel."""
        logger.debug(f"Updating Zwischenziel with ID: {zwischenziel_id}")
        existing = await self.dao.get_by_id(zwischenziel_id)
        if existing is None:
            raise ZwischenzielNotFoundError(zwischenziel_id)
        update_data = ZwischenzielUpdate.model_validate(zwischenziel_data)
        merged_data = {
            "title": existing.title,
            "description": existing.description,
            "lernziel_id": existing.lernziel_id,
            "start_date": existing.start_date,
            "end_date": existing.end_date,
            "accumulated_study_time": existing.accumulated_study_time,
            "status": existing.status,
        }
        merged_data.update(update_data.model_dump(mode="json", exclude_unset=True))
        await self.dao.ensure_lernziel_exists(merged_data["lernziel_id"])
        return await self.dao.update(zwischenziel_id, merged_data)

    async def delete_zwischenziel(self, zwischenziel_id: int) -> Zwischenziel | None:
        """Delete a Zwischenziel by its ID."""
        logger.debug(f"Deleting Zwischenziel with ID: {zwischenziel_id}")
        if await self.dao.has_dependents(zwischenziel_id):
            raise ZwischenzielHasDependentsError(
                f"Zwischenziel {zwischenziel_id} kann wegen Abhängigkeiten nicht gelöscht werden."
            )
        try:
            deleted = await self.dao.delete(zwischenziel_id)
        except IntegrityError as e:
            logger.error(f"IntegrityError while deleting Zwischenziel with ID: {zwischenziel_id}: {e}")
            await self.dao.db.rollback()
            raise ZwischenzielHasDependentsError(
                f"Zwischenziel {zwischenziel_id} kann wegen Abhängigkeiten nicht gelöscht werden."
            ) from e
        if deleted is None:
            raise ZwischenzielNotFoundError(zwischenziel_id)
        return deleted

    async def get_zwischenziele_by_lernziel_id(self, lernziel_id: int) -> list[Zwischenziel]:
        """Retrieve all Zwischenziele associated with a specific Lernziel ID."""
        logger.debug(f"Fetching Zwischenziele for Lernziel ID: {lernziel_id}")
        await self.dao.ensure_lernziel_exists(lernziel_id)
        return await self.dao.get_by_lernziel_id(lernziel_id)


def get_zwischenziele_service(
    session: AsyncSession = Depends(get_session),
) -> ZwischenzieleService:
    """Request-scoped Zwischenziele service."""
    return ZwischenzieleService(session)
