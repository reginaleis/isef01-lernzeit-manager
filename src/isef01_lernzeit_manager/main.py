from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_FILE = PACKAGE_DIR / "templates" / "index.html"
STATIC_DIR = PACKAGE_DIR / "static"

@app.get("/")
def read_root() -> HTMLResponse:
    page = TEMPLATE_FILE.read_text()
    content = "<main><h1>Hello, World!</h1></main>"
    return HTMLResponse(page.replace("  <!-- FastAPI inserts the application content here. -->", content))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")