import datetime

from sqlalchemy import Column, DateTime, Integer, String

from isef01_lernzeit_manager.core.database import Base


class PomodoroModel(Base):
    __tablename__ = "pomodoro_sessions"
    id = Column(Integer, primary_key=True)
    task_name = Column(String)
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
