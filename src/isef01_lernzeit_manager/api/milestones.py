"""
API routes Lernziele.
Lernziele = goals
Zwischenziele = milestones
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/milestones", tags=["milestones"])


@router.get("/{milestone_id}")
async def get_milestone(milestone_id: int) -> dict:
    """Retrieve a milestone by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{milestone_id}")
async def update_milestone(milestone_id: int) -> dict:
    """Update a milestone by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{milestone_id}")
async def delete_milestone(milestone_id: int) -> dict:
    """Delete a milestone by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
