"""Handling of database operations for the pomodoro timer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import PomodoroModel


class PomodoroDataAccess:
    """Data access layer for Pomodoro sessions."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, task_name: str, duration: int) -> PomodoroModel:
        """Create a new Pomodoro session."""
        new_session = PomodoroModel(task_name=task_name, duration=duration)
        self.db_session.add(new_session)
        await self.db_session.commit()
        await self.db_session.refresh(new_session)
        return new_session

    async def get_all_sessions(self) -> list[PomodoroModel]:
        """Retrieve all Pomodoro sessions."""
        result = await self.db_session.execute(select(PomodoroModel))
        return list(result.scalars().all())
