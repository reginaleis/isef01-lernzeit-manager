from datetime import UTC, date, datetime
from typing import Annotated, Literal

from pydantic import BeforeValidator

Status = Literal["not_started", "in_progress", "completed", "overdue"]
ExamType = Literal["Klausur", "Hausarbeit", "Projektarbeit", "Seminararbeit", "Fallstudie", "Workbook", "Thesis"]


def normalize_to_utc_date(value: object) -> date | object | None:
    """Convert date or timestamp input to its UTC calendar date."""
    if value is None or isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        timestamp = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    elif isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        return value

    return timestamp.astimezone(UTC).date()


UTCDate = Annotated[date | None, BeforeValidator(normalize_to_utc_date)]


def normalize_to_utc_datetime(value: object) -> datetime | object | None:
    """Convert date or timestamp input to its UTC calendar datetime."""

    if value is None:
        return value

    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time(), tzinfo=UTC)

    if isinstance(value, datetime):
        timestamp = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    elif isinstance(value, str):
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        return value

    return timestamp.astimezone(UTC)


UTCDateTime = Annotated[datetime | None, BeforeValidator(normalize_to_utc_datetime)]


def check_dates_start_before_end(start_date: date | None, end_date: date | None, name: str | None = None) -> None:
    """Ensure start date is before an end date."""
    if start_date is not None and end_date is not None and end_date < start_date:
        raise ValueError(
            f"Ende {'(' + name + ') ' if name else ''}muss nach Start {'(' + name + ') ' if name else ''}liegen."
            " Invalider Input: {start_date} - {end_date}"
        )
