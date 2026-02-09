from __future__ import annotations

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import now_ts, short_hash
from ..models.trend import Trend

logger = get_logger(__name__)


class NewsAPISource:
    async def fetch(self, limit: int | None = None) -> list[Trend]:
        if not SETTINGS.sources.newsapi_key:
            return []

        try:
            import httpx
        except Exception as exc:  # noqa: BLE001
            logger.warning("httpx missing: %s", exc)
            return []

        max_items = min(limit or SETTINGS.sources.max_trends_per_source, 50)
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "language": "en",
            "pageSize": max_items,
            "apiKey": SETTINGS.sources.newsapi_key,
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("NewsAPI source unavailable: %s", exc)
            return []

        trends: list[Trend] = []
        for article in payload.get("articles", []):
            title = str(article.get("title", "")).strip()
            if not title:
                continue
            trend = Trend(
                id=f"newsapi-{short_hash(title)}",
                title=title,
                summary=str(article.get("description", ""))[:500],
                source="newsapi",
                source_url=str(article.get("url", "")),
                language="en",
                created_at=now_ts(),
            )
            trends.append(trend)

        return trends


newsapi_source = NewsAPISource()
