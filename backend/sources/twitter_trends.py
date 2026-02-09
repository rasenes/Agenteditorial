from __future__ import annotations

from ..core.logger import get_logger
from ..core.utils import now_ts, short_hash
from ..models.trend import Trend

logger = get_logger(__name__)


class TwitterTrendsSource:
    async def fetch(self, limit: int = 15) -> list[Trend]:
        try:
            import feedparser
        except Exception as exc:  # noqa: BLE001
            logger.warning("feedparser missing: %s", exc)
            return []

        feed = "https://news.google.com/rss/search?q=twitter%20trending&hl=en-US&gl=US&ceid=US:en"
        try:
            parsed = feedparser.parse(feed)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Twitter trend fallback unavailable: %s", exc)
            return []

        trends: list[Trend] = []
        for entry in parsed.entries[:limit]:
            title = str(entry.get("title", "")).strip()
            if not title:
                continue
            trends.append(
                Trend(
                    id=f"twitter-{short_hash(title)}",
                    title=title,
                    summary=str(entry.get("summary", ""))[:400],
                    source="twitter_trends",
                    source_url=str(entry.get("link", "")),
                    language="en",
                    created_at=now_ts(),
                    momentum=0.55,
                )
            )

        return trends


twitter_trends_source = TwitterTrendsSource()
