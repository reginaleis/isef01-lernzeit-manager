"""Backend service for Lernziele."""

import logging
from calendar import monthrange
from collections.abc import Mapping
from datetime import date

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.exceptions import LernzielHasDependentsError, LernzielNotFoundError
from isef01_lernzeit_manager.persistence.data_access import LernzieleDAO
from isef01_lernzeit_manager.persistence.database import get_session
from isef01_lernzeit_manager.persistence.tables import Lernziel
from isef01_lernzeit_manager.pydantic_models import LernzieleCreate, LernzieleResponse, LernzieleUpdate
from isef01_lernzeit_manager.pydantic_models.helpers import Status

logger = logging.getLogger(__name__)


def add_calendar_months(value: date, months: int) -> date:
    """Add calendar months while clamping dates to the target month's end."""
    month_index = value.year * 12 + value.month - 1 + months
    year, month_index = divmod(month_index, 12)
    month = month_index + 1
    day = min(value.day, monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


class LernzieleService:
    def __init__(self, db_session: AsyncSession):
        self.dao = LernzieleDAO(db_session)

    async def create_lernziel(
        self,
        lernziel_data: LernzieleCreate | Mapping[str, object],
    ) -> Lernziel:
        """Validate and persist a new Lernziel."""
        logger.debug("Creating Lernziel")
        lernziel = LernzieleCreate.model_validate(lernziel_data)
        return await self.dao.create(lernziel.model_dump(mode="json"))

    async def get_lernziel_by_id(self, lernziel_id: int) -> Lernziel:
        """Retrieve a Lernziel by its ID."""
        logger.debug(f"Fetching Lernziel with ID: {lernziel_id}")
        lernziel = await self.dao.get_by_id(lernziel_id)
        if lernziel is None:
            raise LernzielNotFoundError(lernziel_id)
        return lernziel

    async def update_lernziel(
        self,
        lernziel_id: int,
        lernziel_data: LernzieleUpdate | Mapping[str, object],
    ) -> Lernziel | None:
        """Validate and update an existing Lernziel."""
        logger.debug(f"Updating Lernziel with ID: {lernziel_id}")
        existing = await self.dao.get_by_id(lernziel_id)
        if existing is None:
            raise LernzielNotFoundError(lernziel_id)
        update_data = LernzieleUpdate.model_validate(lernziel_data)
        changes = update_data.model_dump(mode="json", exclude_unset=True)
        merged_data = {
            **LernzieleResponse.model_validate(existing).model_dump(mode="json", exclude={"id"}),
            **changes,
        }
        LernzieleCreate.model_validate(merged_data)
        return await self.dao.update(lernziel_id, changes)

    async def delete_lernziel(self, lernziel_id: int) -> Lernziel | None:
        """Delete a Lernziel by its ID."""
        logger.debug(f"Deleting Lernziel with ID: {lernziel_id}")
        if await self.dao.has_dependents(lernziel_id):
            raise LernzielHasDependentsError(lernziel_id)
        try:
            lernziel = await self.dao.delete(lernziel_id)
        except IntegrityError as error:
            await self.dao.db.rollback()
            raise LernzielHasDependentsError(lernziel_id) from error
        if lernziel is None:
            raise LernzielNotFoundError(lernziel_id)
        return lernziel

    async def get_filtered_lernziele(
        self,
        module_id: str | None = None,
        status: Status | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Lernziel]:
        """Retrieve Lernziele matching the supplied optional filters."""
        logger.debug(
            f"Fetching Lernziele with filters - Module ID: {module_id}, Status: {status}, "
            f"From Date: {from_date}, To Date: {to_date}"
        )
        if from_date is not None and to_date is not None and from_date > to_date:
            raise ValueError(
                f"Keine valide Range. `from_date` darf nicht nach `to_date` liegen. "
                f"Erhaltener Input: {from_date} - {to_date}"
            )
        filters: dict[str, object] = {}
        if module_id is not None:
            filters["module_id"] = module_id
        if status is not None:
            filters["status"] = status
        return await self.dao.get_filtered_lernziele(filters, from_date=from_date, to_date=to_date)


def get_lernziele_service(
    session: AsyncSession = Depends(get_session),
) -> LernzieleService:
    """Request-scoped Lernziele service."""
    return LernzieleService(session)
