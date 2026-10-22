from .data_access import PomodoroDataAccess
from .model import PomodoroModel


class PomodoroService:
    """Service layer for Pomodoro sessions."""

    def __init__(self, data_access: PomodoroDataAccess) -> None:
        self.data_access = data_access

    async def start_new_session(self, task_name: str, duration: int) -> PomodoroModel:
        """Start a new Pomodoro session."""
        if not (1 <= duration <= 60):
            raise ValueError("Duration must be between 1 and 60 minutes.")
        return await self.data_access.create(task_name, duration)
