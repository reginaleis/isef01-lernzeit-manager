from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.core.database import get_db

from .data_access import PomodoroDataAccess
from .models import PomodoroBlock, PomodoroCycle
from .schemas import CycleCreate
from .service import PomodoroService

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> PomodoroService:
    """Dependency to get the PomodoroService with the database session."""
    return PomodoroService(PomodoroDataAccess(db))


@router.post("/")
async def create_cycle(
    data: CycleCreate, service: PomodoroService = Depends(get_service)
) -> PomodoroCycle:
    return await service.create_cycle(
        data.focus_duration, data.break_duration, data.total_rounds
    )


@router.get("/{cycle_id}/status")
async def get_status(
    cycle_id: int, service: PomodoroService = Depends(get_service)
) -> Sequence[PomodoroBlock]:
    return await service.get_cycle_status(cycle_id)


@router.get("/{cycle_id}/current")
async def get_current_block(
    cycle_id: int, service: PomodoroService = Depends(get_service)
) -> PomodoroBlock | dict[str, str]:
    block = await service.get_active_block_with_transition(cycle_id)
    if not block:
        return {"message": "No active block or cycle finished"}
    return block


@router.post("/{cycle_id}/start")
async def start_block(
    cycle_id: int, block_id: int, service: PomodoroService = Depends(get_service)
) -> dict[str, str]:
    try:
        await service.start_block(cycle_id, block_id)
        return {"message": "Block started"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/{cycle_id}/pause")
async def pause_block(
    cycle_id: int,
    accumulated_seconds: int = 0,
    service: PomodoroService = Depends(get_service),
) -> dict[str, str]:
    try:
        await service.pause_block(cycle_id, accumulated_seconds)
        return {"message": "Block paused"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/{cycle_id}/skip")
async def skip_block(
    cycle_id: int, service: PomodoroService = Depends(get_service)
) -> dict[str, str]:
    await service.skip_block(cycle_id)
    return {"message": "Block skipped"}
