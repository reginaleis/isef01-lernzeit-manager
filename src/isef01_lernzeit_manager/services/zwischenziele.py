"""Service Zwischenziele."""

import logging
from collections.abc import Mapping
from datetime import date

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
from isef01_lernzeit_manager.pydantic_models import ZwischenzielCreate, ZwischenzielResponse, ZwischenzielUpdate
from isef01_lernzeit_manager.pydantic_models.helpers import Status

logger = logging.getLogger(__name__)


class ZwischenzieleService:
    def __init__(self, db_session: AsyncSession):
        self.dao = ZwischenzieleDAO(db_session)

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
        changes = update_data.model_dump(mode="json", exclude_unset=True)
        merged_data = {
            **ZwischenzielResponse.model_validate(existing).model_dump(mode="json", exclude={"id"}),
            **changes,
        }
        ZwischenzielCreate.model_validate(merged_data)
        await self.dao.ensure_lernziel_exists(merged_data["lernziel_id"])
        return await self.dao.update(zwischenziel_id, changes)

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

    async def get_filtered_zwischenziele(
        self,
        lernziel_id: int | None = None,
        status: Status | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Zwischenziel]:
        """Retrieve Zwischenziele matching the supplied optional filters."""
        logger.debug(
            f"Fetching Zwischenziele with filters - Lernziel ID: {lernziel_id}, Status: {status}, "
            f"From Date: {from_date}, To Date: {to_date}"
        )
        if from_date is not None and to_date is not None and from_date > to_date:
            raise ValueError("from_date cannot be later than to_date.")
        if lernziel_id is not None:
            await self.dao.ensure_lernziel_exists(lernziel_id)
        filters: dict[str, object] = {}
        if lernziel_id is not None:
            filters["lernziel_id"] = lernziel_id
        if status is not None:
            filters["status"] = status
        return await self.dao.get_filtered_zwischenziele(filters, from_date=from_date, to_date=to_date)


def get_zwischenziele_service(
    session: AsyncSession = Depends(get_session),
) -> ZwischenzieleService:
    """Request-scoped Zwischenziele service."""
    return ZwischenzieleService(session)
