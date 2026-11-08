from .demo import router as demo_router
from .lernzeiten import router as lernzeiten_router
from .lernziele import router as lernziele_router
from .notifications import router as notifications_router
from .timer import router as timer_router
from .zwischenziele import router as zwischenziele_router

__all__ = [
    "demo_router",
    "lernziele_router",
    "lernzeiten_router",
    "zwischenziele_router",
    "timer_router",
    "notifications_router",
]
