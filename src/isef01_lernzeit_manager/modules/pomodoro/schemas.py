"""Pydantic schemas to validate input and output data for the Pomodoro timer."""

from pydantic import BaseModel, Field


class CycleCreate(BaseModel):
    focus_duration: int = Field(
        ..., description="Duration of the focus period in seconds.", gt=0
    )
    break_duration: int = Field(
        ..., description="Duration of the break period in seconds.", gt=0
    )
    total_rounds: int = Field(
        ..., description="Total number of rounds in the Pomodoro cycle.", gt=0
    )


class BlockResponse(BaseModel):
    id: int
    cycle_id: int
    type: str
    status: str
    order: int
    duration_seconds: int
    started_at: str | None = None
    accumulated_seconds: int

    class Config:
        from_attributes = True
