from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.routers import config as config_router

DIST_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist" / "spa"


@asynccontextmanager
async def lifespan(application: FastAPI):
    if DIST_DIR.exists():
        application.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")
    yield


app = FastAPI(title="WS Demo Day API", lifespan=lifespan)

app.include_router(config_router.router, prefix="/api")


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.exception_handler(404)
async def spa_fallback(request, exc):  # noqa: ANN001
    index = DIST_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"detail": "Not found"}, status_code=404)
