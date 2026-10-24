from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .api import (
    analytics_router,
    goals_router,
    milestones_router,
    notifications_router,
    sessions_router,
    timer_router,
)
from .persistence import models as _models  # noqa: F401
from .persistence.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan, title="ISEF01 Lernzeit Manager", version="0.1.0")
PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_FILE = PACKAGE_DIR / "templates" / "index.html"
STATIC_DIR = PACKAGE_DIR / "static"


# --------------
# Module Routers
# --------------

app.include_router(goals_router)
app.include_router(milestones_router)
app.include_router(analytics_router)
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
    return HTMLResponse(
        page.replace(
            "  <!-- FastAPI inserts the application content here. -->", content
        )
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
