from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..agent.orchestrator import orchestrator
from ..core.logger import get_logger
from ..core.utils import now_ts

logger = get_logger(__name__)

router = APIRouter()


@router.get("/fetch")
async def fetch_trends(limit: int = Query(default=20, ge=1, le=100), force_refresh: bool = False):
    try:
        trends = await orchestrator.fetch_trends(limit=limit, force_refresh=force_refresh)
        return {
            "trends": [trend.model_dump() for trend in trends],
            "count": len(trends),
            "fetched_at": now_ts(),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("fetch_trends failed")
        raise HTTPException(status_code=500, detail=f"trends_fetch_failed: {exc}") from exc


@router.get("/analyze/{trend_id}")
async def analyze_trend(trend_id: str):
    try:
        trend, angles, reason = await orchestrator.analyze_trend(trend_id)
        if trend is None:
            raise HTTPException(status_code=404, detail="trend_not_found")
        return {
            "trend": trend.model_dump(),
            "detected_angles": angles,
            "reason": reason,
        }
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("analyze_trend failed")
        raise HTTPException(status_code=500, detail=f"trend_analysis_failed: {exc}") from exc
