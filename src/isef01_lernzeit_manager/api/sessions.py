"""
API routes for manual tracking of study sessions.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/")
def create_session(goal_id: int, milestone_id: int) -> dict:
    """Create a new study session."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/")
def get_sessions() -> dict:
    """Retrieve all study sessions."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
