"""Database models/tables."""

from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from isef01_lernzeit_manager.persistence.database import Base


class StatusZiele(Enum):
    """Enum für den Status von Zwischenzielen oder Lernzielen."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class StatusLernzeit(Enum):
    """Enum für den Status von Lernzeiten."""

    GEPLANT = "geplant"
    ABGESCHLOSSEN = "abgeschlossen"


class Lernzeiten(Base):
    """DB Tabelle Lernzeiten."""

    __tablename__ = "lernzeiten"

    id: Mapped[int] = mapped_column(primary_key=True)
    zwischenziel_id: Mapped[int | None] = mapped_column(ForeignKey("zwischenziele.id"), nullable=True)
    zwischenziel: Mapped["Zwischenziel"] = relationship(back_populates="lernzeiten")
    lernziel_id: Mapped[int | None] = mapped_column(ForeignKey("lernziele.id"), nullable=True)
    lernziel: Mapped["Lernziel"] = relationship(back_populates="lernzeiten")
    planned_start_time: Mapped[str | None] = mapped_column(nullable=True, default=None)
    planned_end_time: Mapped[str | None] = mapped_column(nullable=True, default=None)
    actual_start_time: Mapped[str | None] = mapped_column(nullable=True, default=None)
    actual_end_time: Mapped[str | None] = mapped_column(nullable=True, default=None)
    duration: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    status: Mapped[str] = mapped_column(
        default=StatusLernzeit.GEPLANT.value,
        server_default=StatusLernzeit.GEPLANT.value,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "planned_start_time IS NULL OR planned_end_time IS NULL OR "
            "(julianday(planned_start_time) IS NOT NULL AND julianday(planned_end_time) IS NOT NULL "
            "AND julianday(planned_start_time) < julianday(planned_end_time))",
            name="ck_lernzeiten_planned_start_before_end",
        ),
        CheckConstraint(
            "actual_start_time IS NULL OR actual_end_time IS NULL OR "
            "(julianday(actual_start_time) IS NOT NULL AND julianday(actual_end_time) IS NOT NULL "
            "AND julianday(actual_start_time) < julianday(actual_end_time))",
            name="ck_lernzeiten_actual_start_before_end",
        ),
        CheckConstraint("duration >= 0", name="ck_lernzeiten_duration_nonnegative"),
        Index("idx_lernzeiten_zwischenziel_id", "zwischenziel_id"),
    )


class Zwischenziel(Base):
    """DB Tabelle Zwischenziel."""

    __tablename__ = "zwischenziele"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    lernziel_id: Mapped[int] = mapped_column(ForeignKey("lernziele.id"), nullable=False)
    lernziel: Mapped["Lernziel"] = relationship(back_populates="zwischenziele")
    start_date: Mapped[str | None] = mapped_column(nullable=True)
    end_date: Mapped[str | None] = mapped_column(nullable=True)
    accumulated_study_time: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(
        default=StatusZiele.NOT_STARTED.value,
        server_default=StatusZiele.NOT_STARTED.value,
        nullable=False,
    )
    lernzeiten: Mapped[list[Lernzeiten]] = relationship(back_populates="zwischenziel")

    __table_args__ = (Index("idx_zwischenziele_lernziel_id", "lernziel_id"),)


class Lernziel(Base):
    """DB Tabelle Lernziel."""

    __tablename__ = "lernziele"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    module_id: Mapped[str] = mapped_column(nullable=False)
    exam_type: Mapped[str | None] = mapped_column(nullable=True)
    ects: Mapped[int | None] = mapped_column(nullable=True)
    start_date: Mapped[str | None] = mapped_column(nullable=True)
    end_date: Mapped[str | None] = mapped_column(nullable=True)
    completed_on: Mapped[str | None] = mapped_column(nullable=True)
    accumulated_study_time: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(
        default=StatusZiele.NOT_STARTED.value,
        server_default=StatusZiele.NOT_STARTED.value,
        nullable=False,
    )
    zwischenziele: Mapped[list[Zwischenziel]] = relationship(back_populates="lernziel")
    lernzeiten: Mapped[list[Lernzeiten]] = relationship(back_populates="lernziel")

    __table_args__ = (Index("idx_lernziele_module_id", "module_id"),)
