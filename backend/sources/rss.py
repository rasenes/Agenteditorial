from __future__ import annotations

import asyncio
from dataclasses import dataclass

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import now_ts, short_hash
from ..models.trend import Trend

logger = get_logger(__name__)


@dataclass
class RSSSource:
    feeds: list[str]

    async def fetch(self, limit: int | None = None) -> list[Trend]:
        per_source_limit = limit or SETTINGS.sources.max_trends_per_source

        try:
            import feedparser
        except Exception as exc:  # noqa: BLE001
            logger.warning("feedparser missing: %s", exc)
            return []

        async def parse_feed(url: str) -> list[Trend]:
            try:
                parsed = await asyncio.to_thread(feedparser.parse, url)
                trends: list[Trend] = []
                for entry in parsed.entries[:per_source_limit]:
                    title = str(entry.get("title", "")).strip()
                    if not title:
                        continue
                    summary = str(entry.get("summary", "")).strip()[:500]
                    trend = Trend(
                        id=f"rss-{short_hash(url + title)}",
                        title=title,
                        summary=summary,
                        source="rss",
                        source_url=str(entry.get("link", "")),
                        language="en",
                        created_at=now_ts(),
                    )
                    trends.append(trend)
                return trends
            except Exception as exc:  # noqa: BLE001
                logger.warning("RSS fetch failed for %s: %s", url, exc)
                return []

        results = await asyncio.gather(*(parse_feed(url) for url in self.feeds), return_exceptions=False)
        merged: list[Trend] = []
        for bucket in results:
            merged.extend(bucket)
        return merged


rss_source = RSSSource(feeds=SETTINGS.sources.rss_feeds)
