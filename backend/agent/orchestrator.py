from __future__ import annotations

from pathlib import Path

from ..core.cache import cache
from ..core.logger import get_logger
from ..core.utils import now_ts
from ..models.trend import Trend
from ..models.tweet import ABTestRequest, ABTestResult, GenerateTweetsRequest, GenerateTweetsResponse
from .generator import generator
from .memory_engine import memory_engine
from .remix_engine import remix_engine
from .scoring import scoring_engine
from .trend_analyzer import trend_analyzer

logger = get_logger(__name__)


class EditorialOrchestrator:
    async def fetch_trends(self, limit: int = 40, force_refresh: bool = False) -> list[Trend]:
        if not force_refresh:
            cached = cache.get("trends")
            if cached:
                return cached[:limit]

        trends = await trend_analyzer.fetch_trends(limit=limit)
        cache.set("trends", trends)
        return trends

    async def analyze_trend(self, trend_id: str) -> tuple[Trend | None, list[str], str]:
        trends = await self.fetch_trends(limit=80)
        trend = next((item for item in trends if item.id == trend_id), None)
        if not trend:
            return None, [], "Trend introuvable"
        angles, reason = trend_analyzer.analyze_angles(trend)
        return trend, angles, reason

    async def generate(self, request: GenerateTweetsRequest) -> GenerateTweetsResponse:
        trend = await self._resolve_trend(request)
        candidates = await generator.generate_candidates(request=request, trend=trend)
        ranked = scoring_engine.rank(candidates)

        remixes = []
        if request.include_remix and ranked:
            remixes = [remix_engine.remix(tweet) for tweet in ranked[:2]]
            remix_candidates = []
            for remix in remixes:
                remix_candidates.extend(
                    [
                        remix.shorter,
                        remix.aggressive,
                        remix.ironic,
                        remix.minimalist,
                        remix.punchline,
                    ]
                )
            ranked = scoring_engine.rank(ranked + remix_candidates)

        top3 = ranked[:3]
        memory_engine.register_generation(
            theme=request.theme,
            trend_text=trend.title,
            tweets=top3,
            draft_mode=request.draft_mode,
        )

        metadata = {
            "trend": trend.model_dump(),
            "generated_at": now_ts(),
            "draft_mode": request.draft_mode,
            "memory_stats": memory_engine.get_stats(),
            "best_styles": memory_engine.best_styles(),
        }
        return GenerateTweetsResponse(top3=top3, all_candidates=ranked, remixes=remixes, metadata=metadata)

    async def run_ab_test(self, request: ABTestRequest) -> ABTestResult:
        req_a = GenerateTweetsRequest(
            trend_text=request.trend_text,
            theme=request.theme,
            style=request.variant_a_style,
            count=request.samples,
            include_remix=False,
            draft_mode=True,
        )
        req_b = GenerateTweetsRequest(
            trend_text=request.trend_text,
            theme=request.theme,
            style=request.variant_b_style,
            count=request.samples,
            include_remix=False,
            draft_mode=True,
        )

        result_a = await self.generate(req_a)
        result_b = await self.generate(req_b)

        avg_a = sum(tweet.score for tweet in result_a.top3) / len(result_a.top3)
        avg_b = sum(tweet.score for tweet in result_b.top3) / len(result_b.top3)
        winner = "A" if avg_a >= avg_b else "B"

        payload = {
            "id": f"ab-{int(now_ts() * 1000)}",
            "winner": winner,
            "theme": request.theme,
            "trend_text": request.trend_text,
            "variant_a_style": request.variant_a_style,
            "variant_b_style": request.variant_b_style,
            "variant_a_avg_score": round(avg_a, 4),
            "variant_b_avg_score": round(avg_b, 4),
            "created_at": now_ts(),
        }
        memory_engine.register_ab_test(payload)

        return ABTestResult(
            winner=winner,
            variant_a_avg_score=round(avg_a, 4),
            variant_b_avg_score=round(avg_b, 4),
            variant_a_top=result_a.top3,
            variant_b_top=result_b.top3,
        )

    async def export_csv(self) -> str:
        output = Path("backend/data/exports/history.csv")
        return memory_engine.export_csv(str(output))

    async def _resolve_trend(self, request: GenerateTweetsRequest) -> Trend:
        if request.trend_id:
            trends = await self.fetch_trends(limit=80)
            found = next((item for item in trends if item.id == request.trend_id), None)
            if found:
                return found

        trend_text = request.trend_text or "Global trend"
        trend = Trend(
            id=f"manual-{abs(hash(trend_text))}",
            title=trend_text[:220],
            summary="Trend fournie manuellement",
            source="manual",
            source_url="",
            language=request.language,
            theme=request.theme,
            momentum=0.5,
            viral_angle="insight",
            created_at=now_ts(),
        )
        return trend


orchestrator = EditorialOrchestrator()
