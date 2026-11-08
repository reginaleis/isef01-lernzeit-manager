"""
API routes Zwischenziele.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from isef01_lernzeit_manager.exceptions import (
    LernzielNotFoundError,
    ZwischenzielHasDependentsError,
    ZwischenzielNotFoundError,
)
from isef01_lernzeit_manager.pydantic_models.zwischenziele_models import ZwischenzielResponse, ZwischenzielUpdate
from isef01_lernzeit_manager.services import (
    ZwischenzieleService,
    get_zwischenziele_service,
)

router = APIRouter(prefix="/api/zwischenziele", tags=["zwischenziele"])


@router.post("/", response_model=ZwischenzielResponse, status_code=status.HTTP_201_CREATED)
async def new_zwischenziel(
    zwischenziel: ZwischenzielUpdate,
    service: ZwischenzieleService = Depends(get_zwischenziele_service),
) -> ZwischenzielResponse:
    """Neues Zwischenziel anlegen."""
    try:
        created_zwischenziel = await service.create_zwischenziel(zwischenziel.model_dump())
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return ZwischenzielResponse.model_validate(created_zwischenziel)


@router.get("/", response_model=list[ZwischenzielResponse])
async def get_all_zwischenziele(
    service: ZwischenzieleService = Depends(get_zwischenziele_service),
    lernziel_id: int | None = Query(default=None, ge=1, description="Filter nach Lernziel-ID"),
    from_date: date | None = Query(None, description="Format: YYYY-MM-DD"),
    to_date: date | None = Query(None, description="Format: YYYY-MM-DD"),
) -> list[ZwischenzielResponse]:
    """Alle Zwischenziele abrufen."""
    try:
        zwischenziele = await service.get_filtered_zwischenziele(lernziel_id, from_date, to_date)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return [ZwischenzielResponse.model_validate(zwischenziel) for zwischenziel in zwischenziele]


@router.get("/{zwischenziel_id}", response_model=ZwischenzielResponse)
async def get_zwischenziel(
    zwischenziel_id: int = Path(ge=1), service: ZwischenzieleService = Depends(get_zwischenziele_service)
) -> ZwischenzielResponse:
    """Ein Zwischenziel abrufen."""
    try:
        zwischenziel = await service.get_zwischenziel(zwischenziel_id)
    except ZwischenzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return ZwischenzielResponse.model_validate(zwischenziel)


@router.put("/{zwischenziel_id}", response_model=ZwischenzielResponse)
async def update_zwischenziel(
    update: ZwischenzielUpdate,
    zwischenziel_id: int = Path(ge=1),
    service: ZwischenzieleService = Depends(get_zwischenziele_service),
) -> ZwischenzielResponse:
    """Ein Zwischenziel aktualisieren."""
    try:
        updated_zwischenziel = await service.update_zwischenziel(zwischenziel_id, update.model_dump())
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ZwischenzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return ZwischenzielResponse.model_validate(updated_zwischenziel)


@router.delete("/{zwischenziel_id}", response_model=ZwischenzielResponse)
async def delete_zwischenziel(
    zwischenziel_id: int = Path(ge=1),
    service: ZwischenzieleService = Depends(get_zwischenziele_service),
) -> ZwischenzielResponse:
    """Ein Zwischenziel löschen."""
    try:
        zwischenziel = await service.delete_zwischenziel(zwischenziel_id)
    except ZwischenzielHasDependentsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except ZwischenzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return ZwischenzielResponse.model_validate(zwischenziel)
