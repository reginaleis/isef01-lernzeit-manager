"""Business logic for Lernzeit."""

import logging
from collections.abc import Mapping
from datetime import UTC, datetime

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
        if lernzeit.actual_start_time is not None and lernzeit.actual_end_time is not None:
            data["duration"] = self.calculate_actual_duration(
                lernzeit.actual_start_time,
                lernzeit.actual_end_time,
            )
        await self.dao.ensure_lernziel_exists(data["lernziel_id"])
        await self.dao.ensure_zwischenziel_exists(data["zwischenziel_id"])
        created_lernzeit = await self.dao.create(data)
        await self.dao.recalculate_accumulated_study_times(
            lernziel_ids={created_lernzeit.lernziel_id} if created_lernzeit.lernziel_id is not None else set(),
            zwischenziel_ids=(
                {created_lernzeit.zwischenziel_id} if created_lernzeit.zwischenziel_id is not None else set()
            ),
        )
        return created_lernzeit

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
        old_lernziel_id = existing.lernziel_id
        old_zwischenziel_id = existing.zwischenziel_id
        update_data = LernzeitUpdate.model_validate(lernzeit_data)
        data = update_data.model_dump(mode="json", exclude_unset=True)
        actual_start_time = update_data.actual_start_time if "actual_start_time" in data else existing.actual_start_time
        actual_end_time = update_data.actual_end_time if "actual_end_time" in data else existing.actual_end_time
        if actual_start_time is not None and actual_end_time is not None:
            data["duration"] = self.calculate_actual_duration(actual_start_time, actual_end_time)
        await self.dao.ensure_lernziel_exists(data.get("lernziel_id"))
        await self.dao.ensure_zwischenziel_exists(data.get("zwischenziel_id"))
        updated_lernzeit = await self.dao.update(lernzeit_id, data)
        if updated_lernzeit is None:
            raise LernzeitNotFoundError(lernzeit_id)
        await self.dao.recalculate_accumulated_study_times(
            lernziel_ids={
                lernziel_id
                for lernziel_id in (old_lernziel_id, updated_lernzeit.lernziel_id)
                if lernziel_id is not None
            },
            zwischenziel_ids={
                zwischenziel_id
                for zwischenziel_id in (old_zwischenziel_id, updated_lernzeit.zwischenziel_id)
                if zwischenziel_id is not None
            },
        )
        return updated_lernzeit

    async def delete_lernzeit(self, lernzeit_id: int) -> Lernzeiten:
        """Delete a Lernzeit by its ID."""
        logger.debug(f"Deleting Lernzeit with ID: {lernzeit_id}")
        lernzeit = await self.dao.delete(lernzeit_id)
        if lernzeit is None:
            raise LernzeitNotFoundError(lernzeit_id)
        await self.dao.recalculate_accumulated_study_times(
            lernziel_ids={lernzeit.lernziel_id} if lernzeit.lernziel_id is not None else set(),
            zwischenziel_ids={lernzeit.zwischenziel_id} if lernzeit.zwischenziel_id is not None else set(),
        )
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

    @staticmethod
    def calculate_actual_duration(
        actual_start_time: datetime | str | None,
        actual_end_time: datetime | str | None,
    ) -> int:
        """Calculate actual study time in whole minutes."""
        if actual_start_time is None or actual_end_time is None:
            return 0
        start = LernzeitenService._to_utc_datetime(actual_start_time)
        end = LernzeitenService._to_utc_datetime(actual_end_time)
        return int((end - start).total_seconds() // 60)

    @staticmethod
    def _to_utc_datetime(value: datetime | str) -> datetime:
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


def get_lernzeiten_service(
    session: AsyncSession = Depends(get_session),
) -> LernzeitenService:
    """Request-scoped Lernzeiten service"""
    return LernzeitenService(session)
