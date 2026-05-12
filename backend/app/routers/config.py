from pathlib import Path
import yaml
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from app.settings import settings

router = APIRouter()

_cache: dict = {"data": None, "mtime": 0.0, "etag": ""}


@router.get("/config")
async def get_config(request: Request) -> Response:
    path = Path(settings.config_path)
    mtime = path.stat().st_mtime

    if mtime != _cache["mtime"]:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        _cache["data"] = raw
        _cache["mtime"] = mtime
        _cache["etag"] = str(hash(mtime))

    if request.headers.get("if-none-match") == _cache["etag"]:
        return Response(status_code=304)

    return JSONResponse(
        content=_cache["data"],
        headers={"ETag": _cache["etag"], "Cache-Control": "no-cache"},
    )
