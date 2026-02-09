from __future__ import annotations

import asyncio
import re

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import jaccard_similarity
from ..models.trend import Trend
from ..sources import newsapi_source, reddit_source, rss_source, twitter_trends_source, youtube_trends_source

logger = get_logger(__name__)


class TrendAnalyzer:
    THEME_KEYWORDS: dict[str, list[str]] = {
        "IA": ["ai", "ia", "llm", "openai", "model", "agent"],
        "Tech": ["software", "chip", "cloud", "app", "tech"],
        "Science": ["study", "research", "science", "lab", "discovery"],
        "Sport": ["match", "league", "goal", "sport", "cup"],
        "Politique": ["election", "government", "policy", "president", "parliament"],
        "Business": ["startup", "market", "revenue", "funding", "company"],
        "Crypto": ["bitcoin", "crypto", "ethereum", "blockchain"],
        "Univers": ["space", "nasa", "rocket", "planet", "galaxy"],
        "Culture": ["music", "film", "culture", "artist", "book"],
        "Humour": ["meme", "funny", "satire", "joke"],
        "Faits surprenants": ["unexpected", "bizarre", "surprising", "rare"],
        "Philosophie": ["ethics", "meaning", "philosophy", "thought"],
        "Futur": ["future", "forecast", "2030", "tomorrow", "trend"],
    }

    ANGLE_PATTERNS: dict[str, str] = {
        "contradiction": r"\b(but|however|yet|paradox|while)\b",
        "urgence": r"\b(urgent|alert|breaking|crisis|warning)\b",
        "chiffres": r"\b\d+\b",
        "question": r"\?",
        "surprise": r"\b(unexpected|shocking|never|first|record)\b",
    }

    async def fetch_trends(self, limit: int = 40) -> list[Trend]:
        tasks = [
            rss_source.fetch(limit=limit),
            reddit_source.fetch(limit=limit),
            newsapi_source.fetch(limit=limit),
        ]

        if SETTINGS.sources.enable_twitter_trends:
            tasks.append(twitter_trends_source.fetch(limit=limit // 2))
        if SETTINGS.sources.enable_youtube_trends:
            tasks.append(youtube_trends_source.fetch(limit=limit // 2))

        buckets = await asyncio.gather(*tasks, return_exceptions=True)

        merged: list[Trend] = []
        for bucket in buckets:
            if isinstance(bucket, Exception):
                logger.warning("source bucket error: %s", bucket)
                continue
            merged.extend(bucket)

        enriched = [self._enrich(trend) for trend in merged]
        deduped = self._dedupe(enriched)
        ranked = sorted(deduped, key=lambda t: t.momentum, reverse=True)
        return ranked[:limit]

    def analyze_angles(self, trend: Trend) -> tuple[list[str], str]:
        text = f"{trend.title} {trend.summary}".lower()
        detected = [name for name, pattern in self.ANGLE_PATTERNS.items() if re.search(pattern, text)]
        if not detected:
            detected = ["insight", "opinion", "mirror"]
        reason = f"Angles détectés: {', '.join(detected)}"
        return detected, reason

    def _enrich(self, trend: Trend) -> Trend:
        text = f"{trend.title} {trend.summary}".lower()
        trend.theme = self._detect_theme(text)
        trend.viral_angle = self._detect_primary_angle(text)
        trend.momentum = max(0.25, trend.momentum) + self._momentum_boost(text)
        return trend

    def _detect_theme(self, text: str) -> str:
        best_theme = "IA"
        best_hits = 0
        for theme, keywords in self.THEME_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw in text)
            if hits > best_hits:
                best_hits = hits
                best_theme = theme
        return best_theme

    def _detect_primary_angle(self, text: str) -> str:
        for angle, pattern in self.ANGLE_PATTERNS.items():
            if re.search(pattern, text):
                return angle
        return "insight"

    def _momentum_boost(self, text: str) -> float:
        has_number = 1 if re.search(r"\d", text) else 0
        has_urgency = 1 if re.search(self.ANGLE_PATTERNS["urgence"], text) else 0
        has_surprise = 1 if re.search(self.ANGLE_PATTERNS["surprise"], text) else 0
        return (0.12 * has_number) + (0.2 * has_urgency) + (0.18 * has_surprise)

    def _dedupe(self, trends: list[Trend]) -> list[Trend]:
        kept: list[Trend] = []
        for trend in trends:
            if any(jaccard_similarity(trend.title, existing.title) >= 0.75 for existing in kept):
                continue
            kept.append(trend)
        return kept


trend_analyzer = TrendAnalyzer()
