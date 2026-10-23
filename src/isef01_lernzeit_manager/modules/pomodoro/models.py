import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from isef01_lernzeit_manager.core.database import Base


class BlockType(Enum):
    FOCUS = "focus"
    BREAK = "break"


class BlockStatus(Enum):
    OPEN = "open"
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    PAUSED = "paused"


class PomodoroCycle(Base):
    __tablename__ = "pomodoro_cycles"
    id = Column(Integer, primary_key=True)
    task_name = Column(String)
    focus_duration = Column(Integer)
    break_duration = Column(Integer)
    total_rounds = Column(Integer)


class PomodoroBlock(Base):
    __tablename__ = "pomodoro_blocks"
    id = Column(Integer, primary_key=True)
    cycle_id = Column(Integer, ForeignKey("pomodoro_cycles.id"))
    type = Column(String, default=BlockType.FOCUS.value)
    status = Column(String, default=BlockStatus.OPEN.value)
    order = Column(Integer)
    duration_seconds = Column(Integer)
    started_at = Column(
        DateTime, default=datetime.datetime.now(datetime.UTC), nullable=True
    )
    accumulated_seconds = Column(Integer, default=0)  # time spent before last pause
