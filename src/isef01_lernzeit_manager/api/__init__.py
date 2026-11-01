from .analytics import router as analytics_router
from .demo import router as demo_router
from .lerneinheiten import router as sessions_router
from .lernziele import router as goals_router
from .notifications import router as notifications_router
from .timer import router as timer_router
from .zwischenziele import router as milestones_router

__all__ = [
    "analytics_router",
    "demo_router",
    "goals_router",
    "milestones_router",
    "timer_router",
    "notifications_router",
    "sessions_router",
]
