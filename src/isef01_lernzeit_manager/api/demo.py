"""Demo data API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from isef01_lernzeit_manager.persistence.database import get_session
from isef01_lernzeit_manager.services.demo import DemoService

router = APIRouter(prefix="/api/demo", tags=["demo"])


def get_demo_service(
    session: AsyncSession = Depends(get_session),
) -> DemoService:
    """Provide a request-scoped demo service."""
    return DemoService(session)


@router.post("/resetdata", status_code=status.HTTP_204_NO_CONTENT)
async def reset_data(
    service: DemoService = Depends(get_demo_service),
) -> None:
    """Restore the predefined demo data."""
    await service.reset_data()
