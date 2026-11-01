"""
API routes für die manuelle Erfassung von Lerneinheiten.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/lerneinheiten", tags=["lerneinheiten"])


@router.post("/")
def create_lerneinheit(lernziel_id: int, zwischenziel_id: int) -> dict:
    """Neue Lerneinheit anlegen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/")
def get_lerneinheiten() -> dict:
    """Alle Lerneinheiten abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
