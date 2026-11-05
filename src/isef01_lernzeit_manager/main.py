import logging
import sqlite3
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .logging_config import configure_logging

configure_logging()

from .api import (  # noqa: E402
    demo_router,
    goals_router,
    milestones_router,
    notifications_router,
    sessions_router,
    timer_router,
)
from .persistence.database import Base, engine  # noqa: E402

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.debug("Starting backend application")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.debug("Database tables initialized")
    yield
    await engine.dispose()
    logger.debug("Stopped backend application")


app = FastAPI(lifespan=lifespan, title="ISEF01 Lernzeit Manager", version="0.1.0")
PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_FILE = PACKAGE_DIR / "templates" / "index.html"
STATIC_DIR = PACKAGE_DIR / "static"


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> JSONResponse | Any:
    path = request.url.path

    try:
        response = await call_next(request)

    except Exception as e:
        logger.error("Request failed", extra={"extra_data": {"path": path, "error": str(e)}})
        raise

    if response.status_code >= 400:
        # 1. Read the response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # 2. Log the body
        logger.warning(
            "Request failed",
            extra={
                "extra_data": {
                    "path": path,
                    "status": response.status_code,
                    "response_body": response_body.decode(errors="replace"),
                }
            },
        )

        # 3. IMPORTANT: Reconstruct the response because the iterator is now empty
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    return response


@app.exception_handler(sqlite3.Error)
async def db_exception_handler(request: Request, exc: sqlite3.Error) -> JSONResponse:
    logger.error(f"DB Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "A database error occurred."},
    )


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
def read_root() -> HTMLResponse:
    page = TEMPLATE_FILE.read_text()
    content = "<main><h1>Hello, World!</h1></main>"
    return HTMLResponse(page.replace("  <!-- FastAPI inserts the application content here. -->", content))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
