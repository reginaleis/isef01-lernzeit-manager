"""
Pydantic models für die Validierung von API responses für Zwischenziele.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from isef01_lernzeit_manager.pydantic_models.helpers import Status, UTCDate, check_dates_start_before_end


class ZwischenzielBase(BaseModel):
    """Basis-Schema für Zwischenziele."""

    description: str | None = None
    start_date: UTCDate | None = None
    end_date: UTCDate | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validate_date_range(self) -> "ZwischenzielBase":
        """Ensure a Zwischenziel does not end before it starts."""
        check_dates_start_before_end(self.start_date, self.end_date)
        return self


class ZwischenzielCreate(ZwischenzielBase):
    """Schema für Zwischenziele API-Request."""

    title: str = Field(min_length=1)
    accumulated_study_time: int = Field(ge=0, default=0)
    lernziel_id: int = Field(ge=0)
    status: Status = "not_started"

    model_config = ConfigDict(from_attributes=True)


class ZwischenzielUpdate(ZwischenzielBase):
    """Schema für Zwischenziele API-Request."""

    title: str | None = Field(default=None, min_length=1)
    accumulated_study_time: int | None = Field(default=None, ge=0)
    lernziel_id: int | None = Field(default=None, ge=0)
    status: Status | None = None


class ZwischenzielResponse(ZwischenzielCreate):
    """Schema für Zwischenziele API-Response."""

    id: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)
