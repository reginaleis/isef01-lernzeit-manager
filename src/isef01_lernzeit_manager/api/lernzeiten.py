"""API routes Lernzeiten."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from isef01_lernzeit_manager.exceptions import (
    LernzeitNotFoundError,
    LernzielNotFoundError,
    ZwischenzielNotFoundError,
)
from isef01_lernzeit_manager.pydantic_models import LernzeitCreate, LernzeitResponse, LernzeitUpdate
from isef01_lernzeit_manager.pydantic_models.lernzeiten_models import LernzeitStatus
from isef01_lernzeit_manager.services import LernzeitenService, get_lernzeiten_service

router = APIRouter(prefix="/api/lernzeiten", tags=["lernzeiten"])


@router.post("/", response_model=LernzeitResponse, status_code=status.HTTP_201_CREATED)
async def new_lernzeit(
    lernzeit: LernzeitCreate,
    service: LernzeitenService = Depends(get_lernzeiten_service),
) -> LernzeitResponse:
    """Neue Lernzeit anlegen."""
    try:
        created_lernzeit = await service.create_lernzeit(lernzeit)
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ZwischenzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return LernzeitResponse.model_validate(created_lernzeit)


@router.get("/", response_model=list[LernzeitResponse])
async def get_all_lernzeiten(
    service: LernzeitenService = Depends(get_lernzeiten_service),
    lernziel_id: int | None = Query(default=None, ge=1, description="Filter nach Lernziel-ID"),
    zwischenziel_id: int | None = Query(default=None, ge=1, description="Filter nach Zwischenziel-ID"),
    filter_status: LernzeitStatus | None = Query(default=None, alias="status"),
) -> list[LernzeitResponse]:
    """Alle Lernzeiten oder passend zu den angegebenen Filtern abrufen."""
    try:
        lernzeiten = await service.get_filtered_lernzeiten(lernziel_id, zwischenziel_id, filter_status)
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ZwischenzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return [LernzeitResponse.model_validate(lernzeit) for lernzeit in lernzeiten]


@router.get("/{lernzeit_id}", response_model=LernzeitResponse)
async def get_lernzeit(
    lernzeit_id: int = Path(ge=1),
    service: LernzeitenService = Depends(get_lernzeiten_service),
) -> LernzeitResponse:
    """Eine Lernzeit abrufen."""
    try:
        lernzeit = await service.get_lernzeit_by_id(lernzeit_id)
    except LernzeitNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return LernzeitResponse.model_validate(lernzeit)


@router.put("/{lernzeit_id}", response_model=LernzeitResponse)
async def update_lernzeit(
    update: LernzeitUpdate,
    lernzeit_id: int = Path(ge=1),
    service: LernzeitenService = Depends(get_lernzeiten_service),
) -> LernzeitResponse:
    """Eine Lernzeit aktualisieren."""
    try:
        lernzeit = await service.update_lernzeit(lernzeit_id, update)
    except LernzeitNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except LernzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ZwischenzielNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return LernzeitResponse.model_validate(lernzeit)


@router.delete("/{lernzeit_id}", response_model=LernzeitResponse)
async def delete_lernzeit(
    lernzeit_id: int = Path(ge=1),
    service: LernzeitenService = Depends(get_lernzeiten_service),
) -> LernzeitResponse:
    """Eine Lernzeit löschen."""
    try:
        lernzeit = await service.delete_lernzeit(lernzeit_id)
    except LernzeitNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return LernzeitResponse.model_validate(lernzeit)
