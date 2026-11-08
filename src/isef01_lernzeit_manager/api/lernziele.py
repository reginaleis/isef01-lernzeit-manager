"""
API routes Lernziele.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, status

from isef01_lernzeit_manager.exceptions import LernzielHasDependentsError, LernzielNotFoundError
from isef01_lernzeit_manager.pydantic_models import (
    LernzieleCreate,
    LernzieleResponse,
    LernzieleUpdate,
    ZwischenzielResponse,
)
from isef01_lernzeit_manager.services import (
    LernzieleService,
    get_lernziele_service,
)

router = APIRouter(prefix="/api/lernziele", tags=["lernziele"])


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


@router.get("/next-six-months", response_model=list[LernzieleResponse])
async def get_lernziele_next_6_months(
    service: LernzieleService = Depends(get_lernziele_service),
) -> list[LernzieleResponse]:
    """Lernziele der nächsten 6 Monate abrufen."""
    lernziele = await service.get_lernziele_next_6_months()
    return [LernzieleResponse.model_validate(lernziel) for lernziel in lernziele]


@router.get("/{lernziel_id}", response_model=LernzieleResponse)
async def get_lernziel(
    lernziel_id: int = Path(ge=1),
    service: LernzieleService = Depends(get_lernziele_service),
) -> LernzieleResponse:
    """Lernziel nach ID abrufen."""
    try:
        lernziel = await service.get_lernziel_by_id(lernziel_id)
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return LernzieleResponse.model_validate(lernziel)


@router.put("/{lernziel_id}", response_model=LernzieleResponse)
async def update_lernziel(
    update: LernzieleUpdate,
    lernziel_id: int = Path(ge=1),
    service: LernzieleService = Depends(get_lernziele_service),
) -> LernzieleResponse:
    """Lernziel aktualisieren."""
    try:
        lernziel = await service.update_lernziel(lernziel_id, update)
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return LernzieleResponse.model_validate(lernziel)


@router.delete("/{lernziel_id}", response_model=LernzieleResponse)
async def delete_lernziel(
    lernziel_id: int = Path(ge=1),
    service: LernzieleService = Depends(get_lernziele_service),
) -> LernzieleResponse:
    """Lernziel löschen."""
    try:
        lernziel = await service.delete_lernziel(lernziel_id)
    except LernzielHasDependentsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lernziel kann nicht gelöscht werden, solange Zwischenziele oder Lernzeiten referenziert werden.",
        ) from None
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return LernzieleResponse.model_validate(lernziel)


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
