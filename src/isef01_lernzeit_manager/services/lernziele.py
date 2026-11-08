"""Backend service for Lernziele."""

import logging
from calendar import monthrange
from collections.abc import Mapping
from datetime import UTC, date, datetime

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.exceptions import LernzielHasDependentsError, LernzielNotFoundError
from isef01_lernzeit_manager.persistence.data_access import LernzieleDAO
from isef01_lernzeit_manager.persistence.database import get_session
from isef01_lernzeit_manager.persistence.tables import Lernziel
from isef01_lernzeit_manager.pydantic_models import LernzieleCreate, LernzieleUpdate

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

    async def get_all_lernziele(self) -> list[Lernziel]:
        """Alle Lernziele abrufen."""
        logger.debug("Fetching all Lernziele")
        return await self.dao.get_all()

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
        merged_data = {
            "title": existing.title,
            "description": existing.description,
            "module_id": existing.module_id,
            "start_date": existing.start_date,
            "end_date": existing.end_date,
            "status": existing.status,
            "accumulated_study_time": existing.accumulated_study_time,
            **update_data.model_dump(mode="json", exclude_unset=True),
        }
        LernzieleCreate.model_validate(merged_data)
        return await self.dao.update(lernziel_id, update_data.model_dump(mode="json", exclude_unset=True))

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

    async def get_lernziele_next_6_months(self) -> list[Lernziel]:
        """Retrieve Lernziele for the next 6 months."""
        logger.debug("Fetching Lernziele for the next 6 months")
        today = datetime.now(UTC).date()
        six_months_later = add_calendar_months(today, 6)
        return await self.dao.get_lernziele_in_range(from_date=today, to_date=six_months_later)

    async def get_lernziele_in_range(
        self,
        from_date: date | None,
        to_date: date | None,
    ) -> list[Lernziel]:
        """Retrieve Lernziele within a specific date range."""
        logger.debug(f"Fetching Lernziele from {from_date} to {to_date}")
        if from_date is None:
            earliest_start = await self.dao.get_earliest_start_date()
            if earliest_start is None:
                raise ValueError("`from_date` ist erforderlich, wenn `to_date` angegeben ist.")
            from_date = date.fromisoformat(earliest_start)
        if to_date is None:
            latest_start = await self.dao.get_latest_start_date()
            if latest_start is None:
                raise ValueError("`to_date` ist erforderlich, wenn `from_date` angegeben ist.")
            to_date = date.fromisoformat(latest_start)
        if from_date > to_date:
            raise ValueError(
                f"Keine valide Range. `from_date` muss vor `to_date` liegen. Erhaltener Input: {from_date} - {to_date}"
            )
        return await self.dao.get_lernziele_in_range(from_date=from_date, to_date=to_date)


def get_lernziele_service(
    session: AsyncSession = Depends(get_session),
) -> LernzieleService:
    """Request-scoped Lernziele service."""
    return LernzieleService(session)
