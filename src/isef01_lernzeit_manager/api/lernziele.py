"""
API routes Lernziele.
"""

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from isef01_lernzeit_manager.exceptions import LernzielHasDependentsError, LernzielNotFoundError
from isef01_lernzeit_manager.pydantic_models import (
    LernzieleCreate,
    LernzieleResponse,
    LernzieleUpdate,
)
from isef01_lernzeit_manager.pydantic_models.helpers import Status
from isef01_lernzeit_manager.services import (
    LernzieleService,
    get_lernziele_service,
)
from isef01_lernzeit_manager.services.lernziele import add_calendar_months

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
async def get_filtered_lernziele(
    service: LernzieleService = Depends(get_lernziele_service),
    from_date: date | None = Query(None, description="Format: YYYY-MM-DD"),
    to_date: date | None = Query(None, description="Format: YYYY-MM-DD"),
    module_id: str | None = Query(None, min_length=1, description="Filter nach Modul-ID"),
    filter_status: Status | None = Query(None, alias="status"),
) -> list[LernzieleResponse]:
    """Alle Lernziele oder passend zu den angegebenen Filtern abrufen."""
    try:
        lernziele = await service.get_filtered_lernziele(
            module_id=module_id,
            status=filter_status,
            from_date=from_date,
            to_date=to_date,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return [LernzieleResponse.model_validate(lernziel) for lernziel in lernziele]


@router.get("/next-six-months", response_model=list[LernzieleResponse])
async def get_lernziele_next_6_months(
    service: LernzieleService = Depends(get_lernziele_service),
) -> list[LernzieleResponse]:
    """Lernziele der nächsten 6 Monate abrufen (Kurzform des Startdatumsfilters)."""
    today = datetime.now(UTC).date()
    six_months_later = add_calendar_months(today, 6)
    lernziele = await service.get_filtered_lernziele(from_date=today, to_date=six_months_later)
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
