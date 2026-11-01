"""
Pydantic models für die Validierung von API responses für Lernziele.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LernzieleCreate(BaseModel):
    """Schema für das Anlegen eines Lernziels."""

    title: str = Field(min_length=1)
    description: str | None = None
    module_id: str = Field(min_length=1)
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: Literal["not_started", "in_progress", "completed", "overdue"] = "not_started"
    accumulated_study_time_min: int = Field(default=0, ge=0)


class LernzieleResponse(BaseModel):
    """Schema für Lernziele API-Response."""

    id: int = Field(ge=0)
    title: str = Field(min_length=1)
    description: str | None = None
    module_id: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str
    accumulated_study_time_min: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)


class LernzieleUpdate(BaseModel):
    """Schema für Lernziele API-Update."""

    title: str | None = Field(min_length=1)
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None
    accumulated_study_time_min: int | None = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)
