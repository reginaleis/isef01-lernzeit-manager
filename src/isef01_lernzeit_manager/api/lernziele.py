"""
API routes Lernziele.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.api.pydantic_models import (
    LernzieleCreate,
    LernzieleResponse,
    LernzieleUpdate,
    ZwischenzielResponse,
)
from isef01_lernzeit_manager.persistence.database import get_session
from isef01_lernzeit_manager.services import LernzieleService

router = APIRouter(prefix="/api/lernziele", tags=["lernziele"])


def get_lernziele_service(
    session: AsyncSession = Depends(get_session),
) -> LernzieleService:
    """Request-scoped Lernziele service."""
    return LernzieleService(session)


@router.post("/", response_model=LernzieleResponse, status_code=status.HTTP_201_CREATED)
async def new_lernziel(
    lernziel: LernzieleCreate,
    service: LernzieleService = Depends(get_lernziele_service),
) -> LernzieleResponse:
    """Neues Lernziel anlegen."""
    created_lernziel = await service.create_lernziel(lernziel.model_dump())
    return LernzieleResponse.model_validate(created_lernziel)


@router.get("/", response_model=list[LernzieleResponse])
async def get_all_lernziele(
    service: LernzieleService = Depends(get_lernziele_service),
) -> list[LernzieleResponse]:
    """Alle Lernziele abrufen."""
    lernziele = await service.get_all_lernziele()
    return [LernzieleResponse.model_validate(lernziel) for lernziel in lernziele]


@router.get("/{lernziel_id}", response_model=LernzieleResponse)
async def get_lernziel(lernziel_id: int) -> dict:
    """Lernziel nach ID abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{lernziel_id}", response_model=LernzieleResponse)
async def update_lernziel(lernziel_id: int, update: LernzieleUpdate) -> dict:
    """Lernziel aktualisieren."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{lernziel_id}", response_model=LernzieleResponse)
async def delete_lernziel(lernziel_id: int) -> dict:
    """Lernziel löschen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{lernziel_id}/zwischenziele", response_model=list[ZwischenzielResponse])
async def get_zwischenziele_for_lernziel(lernziel_id: int) -> dict:
    """Zwischenziele eines Lernziels abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{lernziel_id}/zwischenziele/{zwischenziel_id}", response_model=ZwischenzielResponse)
async def get_zwischenziel_for_lernziel(lernziel_id: int, zwischenziel_id: int) -> dict:
    """Ein Zwischenziel eines Lernziels abrufen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/{lernziel_id}/zwischenziele")
async def new_zwischenziel_for_lernziel(lernziel_id: int) -> dict:
    """Neues Zwischenziel für ein Lernziel anlegen."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
