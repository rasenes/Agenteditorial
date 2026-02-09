from __future__ import annotations

from ..core.logger import get_logger
from ..core.utils import now_ts, short_hash
from ..models.trend import Trend

logger = get_logger(__name__)


class YouTubeTrendsSource:
    async def fetch(self, limit: int = 15) -> list[Trend]:
        try:
            import feedparser
        except Exception as exc:  # noqa: BLE001
            logger.warning("feedparser missing: %s", exc)
            return []

        feed = "https://www.youtube.com/feeds/videos.xml?channel_id=UC4R8DWoMoI7CAwX8_LjQHig"
        try:
            parsed = feedparser.parse(feed)
        except Exception as exc:  # noqa: BLE001
            logger.warning("YouTube trends unavailable: %s", exc)
            return []

        trends: list[Trend] = []
        for entry in parsed.entries[:limit]:
            title = str(entry.get("title", "")).strip()
            if not title:
                continue
            trends.append(
                Trend(
                    id=f"youtube-{short_hash(title)}",
                    title=title,
                    summary="Trending YouTube topic",
                    source="youtube_trends",
                    source_url=str(entry.get("link", "")),
                    language="en",
                    created_at=now_ts(),
                    momentum=0.5,
                )
            )

        return trends


youtube_trends_source = YouTubeTrendsSource()
