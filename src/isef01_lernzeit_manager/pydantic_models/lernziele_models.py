"""
Pydantic models für die Validierung von API responses für Lernziele.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from isef01_lernzeit_manager.pydantic_models.helpers import Status, UTCDate, check_dates_start_before_end


class LernzieleBase(BaseModel):
    """Basis-Schema für Lernziele."""

    title: Annotated[str, Field(min_length=1)]
    description: str | None = None
    module_id: Annotated[str, Field(min_length=1)]
    start_date: UTCDate = None
    end_date: UTCDate = None
    status: Status = "not_started"
    accumulated_study_time: int = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_date_range(self) -> "LernzieleBase":
        """Ensure a Lernziel does not end before it starts."""
        check_dates_start_before_end(self.start_date, self.end_date)
        return self


class LernzieleCreate(LernzieleBase):
    """Schema für das Anlegen eines Lernziels."""

    model_config = ConfigDict(extra="forbid")


class LernzieleUpdate(LernzieleBase):
    """Schema für Lernziele API-Update."""

    model_config = ConfigDict(extra="forbid")


class LernzieleResponse(LernzieleBase):
    """Schema für Lernziele API-Response."""

    id: int = Field(ge=1)

    model_config = ConfigDict(from_attributes=True, extra="forbid")
