from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..agent.memory_engine import memory_engine
from ..core.logger import get_logger
from ..models.tweet import FavoriteTweetRequest

logger = get_logger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_memory_stats():
    try:
        return memory_engine.get_stats()
    except Exception as exc:  # noqa: BLE001
        logger.exception("memory stats failed")
        raise HTTPException(status_code=500, detail=f"memory_stats_failed: {exc}") from exc


@router.get("/history")
async def get_history(limit: int = Query(default=50, ge=1, le=300)):
    try:
        rows = memory_engine.list_history(limit=limit)
        return {"items": rows, "count": len(rows)}
    except Exception as exc:  # noqa: BLE001
        logger.exception("memory history failed")
        raise HTTPException(status_code=500, detail=f"memory_history_failed: {exc}") from exc


@router.get("/heatmap")
async def get_heatmap():
    try:
        return {"items": memory_engine.theme_heatmap()}
    except Exception as exc:  # noqa: BLE001
        logger.exception("memory heatmap failed")
        raise HTTPException(status_code=500, detail=f"memory_heatmap_failed: {exc}") from exc


@router.post("/favorite")
async def add_favorite(request: FavoriteTweetRequest):
    try:
        created = memory_engine.add_favorite(request.tweet_id)
        return JSONResponse(
            status_code=201 if created else 200,
            content={"tweet_id": request.tweet_id, "created": created},
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("favorite failed")
        raise HTTPException(status_code=500, detail=f"favorite_failed: {exc}") from exc


@router.get("/export/json")
async def export_json():
    try:
        return memory_engine.export_json()
    except Exception as exc:  # noqa: BLE001
        logger.exception("json export failed")
        raise HTTPException(status_code=500, detail=f"memory_export_json_failed: {exc}") from exc
