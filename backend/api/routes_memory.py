"""
Routes pour la mémoire et l'historique.
"""

from fastapi import APIRouter, HTTPException

from ..agent.memory_engine import memory_engine
from ..core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_memory_stats():
    """Get memory statistics."""
    try:
        stats = memory_engine.get_memory_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_memory():
    """Clear memory (admin only)."""
    try:
        memory_engine.clear()
        return {"status": "cleared"}
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tweets")
async def get_stored_tweets(limit: int = 50):
    """Get recently stored tweets from memory."""
    try:
        # TODO: Fetch from memory
        return {"tweets": [], "count": 0}
    except Exception as e:
        logger.error(f"Failed to get tweets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
