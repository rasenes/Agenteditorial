"""
Routes pour les tendances.
"""

from fastapi import APIRouter, HTTPException

from ..agent.orchestrator import orchestrator
from ..core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/fetch")
async def fetch_trends(limit: int = 10):
    """Fetch latest trends."""
    try:
        trends = await orchestrator.fetch_trends()
        return {
            "trends": [t.to_dict() for t in trends[:limit]],
            "count": len(trends),
        }
    except Exception as e:
        logger.error(f"Fetch trends failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{trend_id}")
async def analyze_trend(trend_id: str):
    """Analyze a trend and extract angles."""
    try:
        # TODO: Get trend from DB and analyze
        return {"angles": []}
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
