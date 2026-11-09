"""
Pydantic models für die Validierung von API responses für Lernziele.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from isef01_lernzeit_manager.pydantic_models.helpers import ExamType, Status, UTCDate, check_dates_start_before_end


class LernzieleBase(BaseModel):
    """Basis-Schema für Lernziele."""

    description: str | None = None
    exam_type: ExamType | None = None
    ects: int | None = Field(default=None, ge=0)
    start_date: UTCDate = None
    end_date: UTCDate = None
    completed_on: UTCDate = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_date_range(self) -> "LernzieleBase":
        """Ensure a Lernziel does not end before it starts."""
        check_dates_start_before_end(self.start_date, self.end_date)
        return self


class LernzieleCreate(LernzieleBase):
    """Schema für das Anlegen eines Lernziels."""

    title: Annotated[str, Field(min_length=1)]
    module_id: Annotated[str, Field(min_length=1)]
    status: Status = "not_started"
    accumulated_study_time: int = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")


class LernzieleUpdate(LernzieleBase):
    """Schema für Lernziele API-Update."""

    title: str | None = Field(default=None, min_length=1)
    module_id: str | None = Field(default=None, min_length=1)
    status: Status | None = None
    accumulated_study_time: int | None = Field(default=None, ge=0)


class LernzieleResponse(LernzieleCreate):
    """Schema für Lernziele API-Response."""

    id: int = Field(ge=1)

    model_config = ConfigDict(from_attributes=True, extra="forbid")
