"""
API routes Application Analytics.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary() -> dict:
    """Retrieve a summary of application analytics."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/progress")
def get_progress() -> dict:
    """Retrieve progress analytics."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
