"""Persistence-related domain exceptions."""


class LernzielNotFoundError(LookupError):
    """Raised when a requested Lernziel does not exist."""

    def __init__(self, lernziel_id: int | str | None):
        super().__init__(f"Das Lernziel mit der ID {lernziel_id} wurde nicht gefunden.")


class ZwischenzielNotFoundError(LookupError):
    """Raised when a requested Zwischenziel does not exist."""

    def __init__(self, zwischenziel_id: int):
        super().__init__(f"Das Zwischenziel mit der ID {zwischenziel_id} wurde nicht gefunden.")


class LernzielHasDependentsError(Exception):
    """Raised when a Lernziel cannot be deleted because children reference it."""


class ZwischenzielHasDependentsError(Exception):
    """Raised when a Zwischenziel cannot be deleted because Lernzeiten reference it."""
