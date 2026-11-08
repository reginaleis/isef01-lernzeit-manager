"""Business logic for Lernzeit."""

import logging
from collections.abc import Mapping

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.exceptions import LernzeitNotFoundError
from isef01_lernzeit_manager.persistence.data_access import LernzeitenDAO
from isef01_lernzeit_manager.persistence.database import get_session
from isef01_lernzeit_manager.persistence.tables import Lernzeiten
from isef01_lernzeit_manager.pydantic_models import LernzeitCreate, LernzeitUpdate
from isef01_lernzeit_manager.pydantic_models.lernzeiten_models import LernzeitStatus

logger = logging.getLogger(__name__)


class LernzeitenService:
    def __init__(self, db_session: AsyncSession):
        self.dao = LernzeitenDAO(db_session)

    async def get_all_lernzeiten(self) -> list[Lernzeiten]:
        """Alle Lernzeiten abfragen."""
        logger.debug("Fetching all Lernzeiten")
        return await self.dao.get_all()

    async def create_lernzeit(
        self,
        lernzeit_data: LernzeitCreate | Mapping[str, object],
    ) -> Lernzeiten:
        """Validate and persist a new Lernzeit."""
        logger.debug("Creating Lernzeit")
        lernzeit = LernzeitCreate.model_validate(lernzeit_data)
        data = lernzeit.model_dump(mode="json")
        await self.dao.ensure_lernziel_exists(data["lernziel_id"])
        await self.dao.ensure_zwischenziel_exists(data["zwischenziel_id"])
        return await self.dao.create(data)

    async def get_lernzeit_by_id(self, lernzeit_id: int) -> Lernzeiten:
        """Retrieve a Lernzeit by its ID."""
        logger.debug(f"Fetching Lernzeit with ID: {lernzeit_id}")
        lernzeit = await self.dao.get_by_id(lernzeit_id)
        if lernzeit is None:
            raise LernzeitNotFoundError(lernzeit_id)
        return lernzeit

    async def update_lernzeit(
        self,
        lernzeit_id: int,
        lernzeit_data: LernzeitUpdate | Mapping[str, object],
    ) -> Lernzeiten:
        """Validate and update an existing Lernzeit."""
        logger.debug(f"Updating Lernzeit with ID: {lernzeit_id}")
        existing = await self.dao.get_by_id(lernzeit_id)
        if existing is None:
            raise LernzeitNotFoundError(lernzeit_id)
        update_data = LernzeitUpdate.model_validate(lernzeit_data)
        data = update_data.model_dump(mode="json", exclude_unset=True)
        await self.dao.ensure_lernziel_exists(data.get("lernziel_id"))
        await self.dao.ensure_zwischenziel_exists(data.get("zwischenziel_id"))
        updated_lernzeit = await self.dao.update(lernzeit_id, data)
        if updated_lernzeit is None:
            raise LernzeitNotFoundError(lernzeit_id)
        return updated_lernzeit

    async def delete_lernzeit(self, lernzeit_id: int) -> Lernzeiten:
        """Delete a Lernzeit by its ID."""
        logger.debug(f"Deleting Lernzeit with ID: {lernzeit_id}")
        lernzeit = await self.dao.delete(lernzeit_id)
        if lernzeit is None:
            raise LernzeitNotFoundError(lernzeit_id)
        return lernzeit

    async def get_filtered_lernzeiten(
        self,
        lernziel_id: int | None = None,
        zwischenziel_id: int | None = None,
        status: LernzeitStatus | None = None,
    ) -> list[Lernzeiten]:
        """Retrieve Lernzeiten matching the supplied optional filters."""
        logger.debug(
            "Fetching Lernzeiten with filters - "
            f"Lernziel ID: {lernziel_id}, Zwischenziel ID: {zwischenziel_id}, Status: {status}"
        )
        await self.dao.ensure_lernziel_exists(lernziel_id)
        await self.dao.ensure_zwischenziel_exists(zwischenziel_id)
        filters: dict[str, object] = {}
        if lernziel_id is not None:
            filters["lernziel_id"] = lernziel_id
        if zwischenziel_id is not None:
            filters["zwischenziel_id"] = zwischenziel_id
        if status is not None:
            filters["status"] = status
        if not filters:
            return await self.dao.get_all()
        return await self.dao.get_filtered_lernzeiten(filters)


def get_lernzeiten_service(
    session: AsyncSession = Depends(get_session),
) -> LernzeitenService:
    """Request-scoped Lernzeiten service"""
    return LernzeitenService(session)
