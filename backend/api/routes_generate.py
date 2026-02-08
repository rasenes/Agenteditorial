"""
Routes pour la génération de tweets.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List

from ..models.tweet import GenerationRequest, Tweet
from ..agent.generator import generator
from ..agent.scoring import scorer
from ..core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/")
async def generate_tweets(request: GenerationRequest):
    """Generate tweets from a trend."""
    try:
        response = await generator.generate(request)
        return response.to_dict()
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def generate_batch(
    trend_ids: Optional[List[str]] = None,
    count_per_trend: int = 3,
):
    """Generate tweets for multiple trends."""
    try:
        # TODO: Fetch trends and generate
        return {"tweets": [], "count": 0}
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score")
async def score_tweets(tweets: List[dict]):
    """Score a list of tweets."""
    try:
        tweet_objects = [Tweet(**t) for t in tweets]
        scored = scorer.sort_tweets(tweet_objects)
        return {
            "tweets": [t.to_dict() for t in scored],
            "count": len(scored),
        }
    except Exception as e:
        logger.error(f"Scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
