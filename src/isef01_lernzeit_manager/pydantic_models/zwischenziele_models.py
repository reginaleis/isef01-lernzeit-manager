"""
Pydantic models für die Validierung von API responses für Zwischenziele.
"""

from pydantic import BaseModel, ConfigDict, Field

from isef01_lernzeit_manager.pydantic_models.helpers import UTCDate


class ZwischenzielResponse(BaseModel):
    """Schema für Zwischenziele API-Response."""

    id: int = Field(ge=0)
    title: str = Field(min_length=1)
    description: str | None = None
    lernziel_id: int = Field(ge=0)
    start_date: UTCDate = None
    accumulated_study_time_min: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)
