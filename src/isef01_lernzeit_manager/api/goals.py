"""
API routes Lernziele.
Lernziele = goals
Zwischenziele = milestones
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.post("/")
async def new_goal() -> dict:
    """Create a new goal."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/")
async def get_all_goals() -> dict:
    """Retrieve all goals."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{goal_id}")
async def get_goal(goal_id: int) -> dict:
    """Retrieve a goal by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{goal_id}")
async def update_goal(goal_id: int) -> dict:
    """Update a goal by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{goal_id}")
async def delete_goal(goal_id: int) -> dict:
    """Delete a goal by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{goal_id}/milestones")
async def get_milestones(goal_id: int) -> dict:
    """Retrieve milestones for a goal by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/{goal_id}/milestones")
async def new_milestone(goal_id: int) -> dict:
    """Create a new milestone for a goal by its ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
