"""Database models/tables."""

from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from isef01_lernzeit_manager.persistence.database import Base


class Status(Enum):
    """Enum for the status of a Zwischenziel or a Lernziel."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Lernzeiten(Base):
    """Database model for Lernzeiten."""

    __tablename__ = "lernzeiten"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zwischenziel_id: Mapped[int | None] = mapped_column(
        ForeignKey("zwischenziele.id"), nullable=True
    )
    lernziel_id: Mapped[int] = mapped_column(ForeignKey("lernziele.id"), nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    zwischenziel: Mapped["Zwischenziel | None"] = relationship(
        back_populates="tracked_lernzeiten"
    )
    lernziel: Mapped["Lernziel"] = relationship(back_populates="tracked_lernzeiten")


class Zwischenziel(Base):
    """Database model for Zwischenziel."""

    __tablename__ = "zwischenziele"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    lernziel_id: Mapped[int] = mapped_column(ForeignKey("lernziele.id"), nullable=False)
    start_date: Mapped[str | None] = mapped_column(nullable=True)
    end_date: Mapped[str | None] = mapped_column(nullable=True)
    accumulated_study_time: Mapped[int] = mapped_column(default=0)
    tracked_lernzeiten: Mapped[list[Lernzeiten]] = relationship(
        back_populates="zwischenziel",
    )
    status: Mapped[str] = mapped_column(
        default=Status.NOT_STARTED.value, nullable=False
    )


class Lernziel(Base):
    """Database model for Lernziel."""

    __tablename__ = "lernziele"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    module_id: Mapped[str] = mapped_column(nullable=False)
    start_date: Mapped[str | None] = mapped_column(nullable=True)
    end_date: Mapped[str | None] = mapped_column(nullable=True)
    accumulated_study_time: Mapped[int] = mapped_column(default=0)
    tracked_lernzeiten: Mapped[list[Lernzeiten]] = relationship(
        back_populates="lernziel",
    )
    status: Mapped[str] = mapped_column(
        default=Status.NOT_STARTED.value, nullable=False
    )
