"""
API routes Timer.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/timer", tags=["timer"])


@router.post("/start")
async def start_timer() -> dict:
    """Starte neuen Timer."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/stop")
async def stop_timer() -> dict:
    """Stoppe den aktuellen Timer."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/active")
async def get_active_timer() -> dict:
    """Aktiven Timer abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
