"""
API routes Lernziele.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/lernziele", tags=["lernziele"])


@router.post("/")
async def new_lernziel() -> dict:
    """Neues Lernziel anlegen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/")
async def get_all_lernziele() -> dict:
    """Alle Lernziele abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{lernziel_id}")
async def get_lernziel(lernziel_id: int) -> dict:
    """Lernziel nach ID abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{lernziel_id}")
async def update_lernziel(lernziel_id: int) -> dict:
    """Lernziel aktualisieren."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{lernziel_id}")
async def delete_lernziel(lernziel_id: int) -> dict:
    """Lernziel löschen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{lernziel_id}/zwischenziele")
async def get_zwischenziele(lernziel_id: int) -> dict:
    """Zwischenziele eines Lernziels abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/{lernziel_id}/zwischenziele")
async def new_zwischenziel(lernziel_id: int) -> dict:
    """Neues Zwischenziel für ein Lernziel anlegen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
