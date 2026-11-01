from datetime import datetime


def check_dates_start_before_end(start_date: datetime | None, end_date: datetime | None) -> None:
    """Ensure a Lernziel does not end before it starts."""
    if start_date is not None and end_date is not None and end_date < start_date:
        raise ValueError("end_date muss nach start_date liegen.")
