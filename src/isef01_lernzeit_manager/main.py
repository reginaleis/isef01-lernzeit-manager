import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from .api import (
    demo_router,
    goals_router,
    milestones_router,
    notifications_router,
    sessions_router,
    timer_router,
)
from .logging_config import configure_logging
from .persistence.database import Base, engine, migrate_database

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting backend application")
    async with engine.begin() as conn:
        await conn.run_sync(migrate_database)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
    yield
    await engine.dispose()
    logger.info("Stopped backend application")


app = FastAPI(lifespan=lifespan, title="ISEF01 Lernzeit Manager", version="0.1.0")
PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_FILE = PACKAGE_DIR / "templates" / "index.html"
STATIC_DIR = PACKAGE_DIR / "static"


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Log every HTTP request handled by the backend."""
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("%s %s failed", request.method, request.url.path)
        raise

    duration = perf_counter() - started_at
    logger.info(
        "%s %s -> %s (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


# --------------
# Module Routers
# --------------

app.include_router(goals_router)
app.include_router(milestones_router)
app.include_router(demo_router)
app.include_router(timer_router)
app.include_router(notifications_router)
app.include_router(sessions_router)

# ------------------------------
# Main Application API Endpoints
# ------------------------------


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Willkommen in der ISEF01 Lernzeit Manager API. Unter /docs gibt's die API Dokumentation.",
        "status": "ok",
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
