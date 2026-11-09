"""Pydantic models für Lernzeiten."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from isef01_lernzeit_manager.pydantic_models.helpers import UTCDateTime, check_dates_start_before_end

LernzeitStatus = Literal["geplant", "abgeschlossen"]


class LernzeitBase(BaseModel):
    """Basis-Schema für Lernzeiten."""

    zwischenziel_id: int | None = Field(ge=0, default=None)
    lernziel_id: int | None = Field(ge=0, default=None)
    planned_start_time: UTCDateTime = None
    planned_end_time: UTCDateTime = None
    actual_start_time: UTCDateTime = None
    actual_end_time: UTCDateTime = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validate_time_ranges(self) -> "LernzeitBase":
        """Ensure planned and actual sessions have valid time ranges."""
        for start, end, name in (
            (self.planned_start_time, self.planned_end_time, "planned"),
            (self.actual_start_time, self.actual_end_time, "actual"),
        ):
            check_dates_start_before_end(start_date=start, end_date=end, name=name)
        return self


class LernzeitCreate(LernzeitBase):
    duration: int = Field(default=0, ge=0, description="Actual study time in whole minutes")
    status: LernzeitStatus = "geplant"


class LernzeitUpdate(LernzeitBase):
    duration: int | None = Field(default=None, ge=0, description="Actual study time in whole minutes")
    status: LernzeitStatus | None = None


class LernzeitResponse(LernzeitCreate):
    id: int = Field(ge=0)
