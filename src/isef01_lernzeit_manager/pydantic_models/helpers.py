from datetime import UTC, date, datetime
from typing import Annotated

from pydantic import BeforeValidator


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


def check_dates_start_before_end(start_date: date | None, end_date: date | None) -> None:
    """Ensure a Lernziel does not end before it starts."""
    if start_date is not None and end_date is not None and end_date < start_date:
        raise ValueError("end_date muss nach start_date liegen.")
