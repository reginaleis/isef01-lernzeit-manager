"""
Pydantic models für die Validierung von API responses für Zwischenziele.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ZwischenzielResponse(BaseModel):
    """Schema für Zwischenziele API-Response."""

    id: int = Field(ge=0)
    title: str = Field(min_length=1)
    description: str | None = None
    lernziel_id: int = Field(ge=0)
    start_date: datetime | None = None
    accumulated_study_time_min: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)
