from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..agent.memory_engine import memory_engine
from ..agent.orchestrator import orchestrator
from ..core.logger import get_logger
from ..models.tweet import GenerateTweetsRequest

logger = get_logger(__name__)

router = APIRouter()


@router.post("/pipeline")
async def run_pipeline(num_trends: int = 5, tweets_per_trend: int = 9):
    try:
        trends = await orchestrator.fetch_trends(limit=num_trends)
        generated = []
        for trend in trends:
            request = GenerateTweetsRequest(
                trend_id=trend.id,
                theme=trend.theme,
                style="insight",
                count=tweets_per_trend,
                include_remix=True,
                draft_mode=False,
            )
            result = await orchestrator.generate(request)
            generated.append(
                {
                    "trend_id": trend.id,
                    "trend_title": trend.title,
                    "top3": [tweet.model_dump() for tweet in result.top3],
                }
            )
        return {"status": "ok", "trends": len(trends), "runs": generated}
    except Exception as exc:  # noqa: BLE001
        logger.exception("pipeline failed")
        raise HTTPException(status_code=500, detail=f"pipeline_failed: {exc}") from exc


@router.get("/status")
async def get_status():
    try:
        stats = memory_engine.get_stats()
        return {"status": "ready", "memory": stats}
    except Exception as exc:  # noqa: BLE001
        logger.exception("status failed")
        raise HTTPException(status_code=500, detail=f"status_failed: {exc}") from exc


@router.post("/memory/clear")
async def clear_memory():
    try:
        memory_engine.clear()
        return {"status": "cleared"}
    except Exception as exc:  # noqa: BLE001
        logger.exception("clear memory failed")
        raise HTTPException(status_code=500, detail=f"memory_clear_failed: {exc}") from exc


@router.get("/export/csv")
async def export_csv():
    try:
        path = await orchestrator.export_csv()
        return {"path": path}
    except Exception as exc:  # noqa: BLE001
        logger.exception("csv export failed")
        raise HTTPException(status_code=500, detail=f"memory_export_csv_failed: {exc}") from exc
