from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..agent.orchestrator import orchestrator
from ..agent.scoring import scoring_engine
from ..core.logger import get_logger
from ..models.tweet import ABTestRequest, GenerateTweetsRequest, TweetCandidate

logger = get_logger(__name__)

router = APIRouter()


@router.post("/")
async def generate_tweets(request: GenerateTweetsRequest):
    try:
        return (await orchestrator.generate(request)).model_dump()
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_tweets failed")
        raise HTTPException(status_code=500, detail=f"generation_failed: {exc}") from exc


@router.post("/score")
async def score_tweets(tweets: list[TweetCandidate]):
    try:
        ranked = scoring_engine.rank(tweets)
        return {
            "top3": [tweet.model_dump() for tweet in ranked[:3]],
            "count": len(ranked),
            "tweets": [tweet.model_dump() for tweet in ranked],
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("score_tweets failed")
        raise HTTPException(status_code=500, detail=f"scoring_failed: {exc}") from exc


@router.post("/ab-test")
async def run_ab_test(request: ABTestRequest):
    try:
        result = await orchestrator.run_ab_test(request)
        return result.model_dump()
    except Exception as exc:  # noqa: BLE001
        logger.exception("ab test failed")
        raise HTTPException(status_code=500, detail=f"ab_test_failed: {exc}") from exc
