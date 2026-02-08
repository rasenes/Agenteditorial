"""
Routes d'administration et pipelines.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..agent.orchestrator import orchestrator
from ..core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/pipeline")
async def run_pipeline(
    num_trends: int = 5,
    tweets_per_trend: int = 3,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Run the full editorial pipeline."""
    try:
        result = await orchestrator.full_pipeline(
            num_trends=num_trends,
            tweets_per_trend=tweets_per_trend,
            create_remixes=True,
        )
        return result
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get pipeline status."""
    try:
        return {
            "status": "ready",
            "initialized": True,
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
