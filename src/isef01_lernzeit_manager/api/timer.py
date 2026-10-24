"""
API routes Pomodoro Timer.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/timer", tags=["timer"])


@router.post("/start")
async def start_timer() -> dict:
    """Start a new timer."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/stop")
async def stop_timer() -> dict:
    """Stop the current timer."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/active")
async def get_active_timer() -> dict:
    """Retrieve the currently active timer."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
