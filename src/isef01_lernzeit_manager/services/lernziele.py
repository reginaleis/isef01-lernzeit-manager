"""Backend service for Lernziele."""

import logging
from calendar import monthrange
from collections.abc import Mapping
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.data_access import LernzieleDAO
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

    async def get_lernziel_by_id(self, lernziel_id: int) -> Lernziel | None:
        """Retrieve a Lernziel by its ID."""
        logger.info(f"Fetching Lernziel with ID: {lernziel_id}")
        return await self.dao.get_by_id(lernziel_id)

    async def update_lernziel(
        self,
        lernziel_id: int,
        lernziel_data: LernzieleUpdate | Mapping[str, object],
    ) -> Lernziel | None:
        """Validate and update an existing Lernziel."""
        logger.info(f"Updating Lernziel with ID: {lernziel_id}")
        existing = await self.dao.get_by_id(lernziel_id)
        if existing is None:
            return None
        update_data = LernzieleUpdate.model_validate(lernziel_data)
        merged_data = {
            "title": existing.title,
            "description": existing.description,
            "module_id": existing.module_id,
            "start_date": existing.start_date,
            "end_date": existing.end_date,
            "status": existing.status,
            "accumulated_study_time_min": existing.accumulated_study_time_min,
            **update_data.model_dump(mode="json", exclude_unset=True),
        }
        LernzieleCreate.model_validate(merged_data)
        return await self.dao.update(lernziel_id, update_data.model_dump(mode="json", exclude_unset=True))

    async def delete_lernziel(self, lernziel_id: int) -> Lernziel | None:
        """Delete a Lernziel by its ID."""
        logger.info(f"Deleting Lernziel with ID: {lernziel_id}")
        return await self.dao.delete(lernziel_id)

    async def get_lernziele_next_6_months(self) -> list[Lernziel]:
        """Retrieve Lernziele for the next 6 months."""
        logger.info("Fetching Lernziele for the next 6 months")
        today = datetime.now(UTC).date()
        six_months_later = add_calendar_months(today, 6)
        return await self.dao.get_lernziele_in_range(from_date=today, to_date=six_months_later)
