from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.core.database import get_db

from .data_access import PomodoroDataAccess
from .model import PomodoroModel
from .service import PomodoroService

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


@router.post("/start")
async def start_pomodoro(
    task_name: str,
    duration: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PomodoroModel:
    """Start a new Pomodoro session."""
    data_access = PomodoroDataAccess(db)
    service = PomodoroService(data_access)
    return await service.start_new_session(task_name, duration)
