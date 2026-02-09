from __future__ import annotations

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import now_ts, short_hash
from ..models.trend import Trend

logger = get_logger(__name__)


class RedditSource:
    async def fetch(self, limit: int | None = None) -> list[Trend]:
        try:
            import httpx
        except Exception as exc:  # noqa: BLE001
            logger.warning("httpx missing: %s", exc)
            return []

        max_items = limit or SETTINGS.sources.max_trends_per_source
        headers = {"User-Agent": SETTINGS.sources.reddit_user_agent}
        url = f"https://www.reddit.com/r/worldnews/top.json?t=day&limit={max_items}"

        try:
            async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Reddit source unavailable: %s", exc)
            return []

        trends: list[Trend] = []
        for child in payload.get("data", {}).get("children", []):
            data = child.get("data", {})
            title = str(data.get("title", "")).strip()
            if not title:
                continue
            trend = Trend(
                id=f"reddit-{short_hash(title)}",
                title=title,
                summary=str(data.get("selftext", ""))[:500],
                source="reddit",
                source_url=f"https://reddit.com{data.get('permalink', '')}",
                language="en",
                created_at=now_ts(),
                momentum=float(data.get("ups", 0)) / 1000.0,
            )
            trends.append(trend)

        return trends


reddit_source = RedditSource()
