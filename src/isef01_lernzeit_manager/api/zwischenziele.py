"""
API routes Zwischenziele.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/zwischenziele", tags=["zwischenziele"])


@router.get("/{zwischenziel_id}")
async def get_zwischenziel(zwischenziel_id: int) -> dict:
    """Ein Zwischenziel abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{zwischenziel_id}")
async def update_zwischenziel(zwischenziel_id: int) -> dict:
    """Ein Zwischenziel aktualisieren."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{zwischenziel_id}")
async def delete_zwischenziel(zwischenziel_id: int) -> dict:
    """Ein Zwischenziel löschen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
