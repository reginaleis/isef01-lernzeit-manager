"""Database models/tables."""

from enum import Enum

from sqlalchemy import (
    REAL,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from isef01_lernzeit_manager.persistence.database import Base


class Status(Enum):
    """Enum for the status of a Zwischenziel or a Lernziel."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Module(Base):
    """Database model for Module."""

    __tablename__ = "module"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    ects: Mapped[float] = mapped_column(REAL, nullable=False)
    exam_type: Mapped[str] = mapped_column(nullable=True)
    completed_on: Mapped[str | None] = mapped_column(nullable=True)
    lernziele: Mapped[list["Lernziel"]] = relationship(
        back_populates="module",
        cascade="all, delete-orphan",
    )


class Lernzeiten(Base):
    """Database model for Lernzeiten."""

    __tablename__ = "lernzeiten"

    id: Mapped[int] = mapped_column(primary_key=True)
    zwischenziel_id: Mapped[int | None] = mapped_column(nullable=True)
    lernziel_id: Mapped[int] = mapped_column(ForeignKey("lernziele.id"), nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    zwischenziel: Mapped["Zwischenziel | None"] = relationship(
        back_populates="tracked_lernzeiten",
        overlaps="lernziel,tracked_lernzeiten",
    )
    lernziel: Mapped["Lernziel"] = relationship(
        back_populates="tracked_lernzeiten",
        overlaps="zwischenziel",
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["zwischenziel_id", "lernziel_id"],
            ["zwischenziele.id", "zwischenziele.lernziel_id"],
        ),
        Index("idx_lernzeiten_lernziel_datum", "lernziel_id", "date"),
        Index("idx_lernzeiten_zwischenziel_id", "zwischenziel_id"),
    )


class Zwischenziel(Base):
    """Database model for Zwischenziel."""

    __tablename__ = "zwischenziele"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    lernziel_id: Mapped[int] = mapped_column(ForeignKey("lernziele.id"), nullable=False)
    start_date: Mapped[str | None] = mapped_column(nullable=True)
    end_date: Mapped[str | None] = mapped_column(nullable=True)
    accumulated_study_time: Mapped[int] = mapped_column(default=0)
    tracked_lernzeiten: Mapped[list[Lernzeiten]] = relationship(
        back_populates="zwischenziel",
        overlaps="lernziel",
    )
    status: Mapped[str] = mapped_column(
        default=Status.NOT_STARTED.value,
        server_default=Status.NOT_STARTED.value,
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint("id", "lernziel_id"),
        Index("idx_zwischenziele_lernziel_id", "lernziel_id"),
    )


class Lernziel(Base):
    """Database model for Lernziel."""

    __tablename__ = "lernziele"

    id: Mapped[int] = mapped_column(primary_key=True)
    module: Mapped["Module"] = relationship(back_populates="lernziele")
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    module_id: Mapped[str] = mapped_column(ForeignKey("module.id"), nullable=False)
    start_date: Mapped[str | None] = mapped_column(nullable=True)
    end_date: Mapped[str | None] = mapped_column(nullable=True)
    accumulated_study_time: Mapped[int] = mapped_column(default=0)
    tracked_lernzeiten: Mapped[list[Lernzeiten]] = relationship(
        back_populates="lernziel",
        overlaps="tracked_lernzeiten,zwischenziel",
    )
    status: Mapped[str] = mapped_column(
        default=Status.NOT_STARTED.value,
        server_default=Status.NOT_STARTED.value,
        nullable=False,
    )
    __table_args__ = (Index("idx_lernziele_module_id", "module_id"),)
