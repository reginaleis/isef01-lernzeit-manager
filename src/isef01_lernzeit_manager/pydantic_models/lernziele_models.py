"""
Pydantic models für die Validierung von API responses für Lernziele.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from isef01_lernzeit_manager.pydantic_models.helpers import UTCDate, check_dates_start_before_end

LernzielStatus = Literal["not_started", "in_progress", "completed", "overdue"]


class LernzieleCreate(BaseModel):
    """Schema für das Anlegen eines Lernziels."""

    title: Annotated[str, Field(min_length=1)]
    description: str | None = None
    module_id: Annotated[str, Field(min_length=1)]
    start_date: UTCDate = None
    end_date: UTCDate = None
    status: LernzielStatus = "not_started"
    accumulated_study_time_min: int = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_date_range(self) -> "LernzieleCreate":
        """Ensure a Lernziel does not end before it starts."""
        check_dates_start_before_end(self.start_date, self.end_date)
        return self


class LernzieleResponse(BaseModel):
    """Schema für Lernziele API-Response."""

    id: int = Field(ge=1)
    title: Annotated[str, Field(min_length=1)]
    description: str | None = None
    module_id: Annotated[str, Field(min_length=1)]
    start_date: UTCDate = None
    end_date: UTCDate = None
    status: LernzielStatus
    accumulated_study_time_min: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    @model_validator(mode="after")
    def validate_date_range(self) -> "LernzieleResponse":
        """Ensure a Lernziel does not end before it starts."""
        check_dates_start_before_end(self.start_date, self.end_date)
        return self


class LernzieleUpdate(BaseModel):
    """Schema für Lernziele API-Update."""

    title: Annotated[str, Field(min_length=1)] | None = None
    description: str | None = None
    start_date: UTCDate = None
    end_date: UTCDate = None
    status: LernzielStatus | None = None
    accumulated_study_time_min: int | None = Field(default=None, ge=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_date_range(self) -> "LernzieleUpdate":
        check_dates_start_before_end(self.start_date, self.end_date)
        return self
