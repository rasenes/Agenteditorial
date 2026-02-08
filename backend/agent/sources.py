"""
Connecteurs pour les sources de tendances :
RSS, Reddit, NewsAPI, Twitter Trends, YouTube Trends.
"""

import asyncio
from typing import List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

from ..core.logger import get_logger
from ..core.utils import async_retry
from ..models.tweet import Trend

logger = get_logger(__name__)


class SourceConnector(ABC):
    """Connecteur abstrait pour sources de tendances."""
    
    @abstractmethod
    async def fetch_trends(self) -> List[Trend]:
        """Récupère les tendances de la source."""
        pass
    
    async def format_trend(self, title: str, description: str = "", **kwargs) -> Trend:
        """Formate une tendance."""
        return Trend(
            title=title,
            description=description,
            source=self.__class__.__name__,
            language=kwargs.get("language", "en"),
            **kwargs
        )


class RSSConnector(SourceConnector):
    """Connecteur RSS pour récupérer l'actualité."""
    
    def __init__(self, feeds: List[str]):
        self.feeds = feeds or []
    
    @async_retry(max_attempts=2, delay=1.0, exceptions=(Exception,))
    async def fetch_trends(self) -> List[Trend]:
        """Récupère les tendances depuis RSS."""
        if not self.feeds:
            logger.warning("No RSS feeds configured")
            return []
        
        try:
            import feedparser
            
            trends = []
            for feed_url in self.feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:5]:  # Top 5 par feed
                        trend = await self.format_trend(
                            title=entry.get("title", ""),
                            description=entry.get("summary", "")[:200],
                            url=entry.get("link", ""),
                            trending_score=0.7,
                        )
                        trends.append(trend)
                except Exception as e:
                    logger.warning(f"Failed to parse feed {feed_url}: {e}")
            
            return trends
        except ImportError:
            logger.error("feedparser not installed")
            return []
        except Exception as e:
            logger.error(f"RSS fetch failed: {e}")
            return []


class RedditConnector(SourceConnector):
    """Connecteur Reddit pour trending topics."""
    
    def __init__(self, subreddits: List[str] = None):
        self.subreddits = subreddits or ["trending", "worldnews", "technology"]
    
    @async_retry(max_attempts=2, delay=1.0, exceptions=(Exception,))
    async def fetch_trends(self) -> List[Trend]:
        """Récupère les tendances depuis Reddit."""
        try:
            import aiohttp
            
            trends = []
            
            async with aiohttp.ClientSession() as session:
                for subreddit in self.subreddits:
                    try:
                        url = f"https://www.reddit.com/r/{subreddit}/top.json?t=day"
                        
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                for post in data.get("data", {}).get("children", [])[:5]:
                                    post_data = post.get("data", {})
                                    trend = await self.format_trend(
                                        title=post_data.get("title", ""),
                                        description=post_data.get("selftext", "")[:200],
                                        url=f"https://reddit.com{post_data.get('permalink', '')}",
                                        trending_score=post_data.get("score", 0) / 10000,
                                        engagement=post_data.get("score", 0),
                                    )
                                    trends.append(trend)
                    except Exception as e:
                        logger.warning(f"Failed to fetch Reddit r/{subreddit}: {e}")
            
            return trends
        except ImportError:
            logger.error("aiohttp not installed")
            return []
        except Exception as e:
            logger.error(f"Reddit fetch failed: {e}")
            return []


class NewsAPIConnector(SourceConnector):
    """Connecteur NewsAPI."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @async_retry(max_attempts=2, delay=1.0, exceptions=(Exception,))
    async def fetch_trends(self) -> List[Trend]:
        """Récupère les tendances depuis NewsAPI."""
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []
        
        try:
            import aiohttp
            
            trends = []
            
            async with aiohttp.ClientSession() as session:
                url = "https://newsapi.org/v2/top-headlines"
                params = {
                    "apiKey": self.api_key,
                    "language": "en",
                    "sortBy": "popularity",
                    "pageSize": 20,
                }
                
                try:
                    async with session.get(url, params=params, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for article in data.get("articles", [])[:10]:
                                trend = await self.format_trend(
                                    title=article.get("title", ""),
                                    description=article.get("description", "")[:200],
                                    url=article.get("url", ""),
                                    trending_score=0.75,
                                )
                                trends.append(trend)
                except Exception as e:
                    logger.warning(f"Failed to fetch NewsAPI: {e}")
            
            return trends
        except ImportError:
            logger.error("aiohttp not installed")
            return []
        except Exception as e:
            logger.error(f"NewsAPI fetch failed: {e}")
            return []


class TwitterTrendsConnector(SourceConnector):
    """Connecteur Twitter/X Trends (stub - nécessite API)."""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
    
    async def fetch_trends(self) -> List[Trend]:
        """Récupère les tendances Twitter."""
        # Nécessite authentification Twitter - stub pour maintenant
        logger.info("Twitter Trends connector (needs Twitter API credentials)")
        return []


class YouTubeTrendsConnector(SourceConnector):
    """Connecteur YouTube Trends."""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
    
    async def fetch_trends(self) -> List[Trend]:
        """Récupère les vidéos trends YouTube."""
        if not self.api_key:
            logger.warning("YouTube API key not configured")
            return []
        
        # Stub - nécessite YoutTube API
        logger.info("YouTube Trends connector (needs YouTube API credentials)")
        return []


class MultiSourceTrendFetcher:
    """Aggrégateur multi-source pour les tendances."""
    
    def __init__(self):
        self.connectors: List[SourceConnector] = []
    
    def add_connector(self, connector: SourceConnector) -> None:
        """Ajoute un connecteur."""
        self.connectors.append(connector)
    
    async def fetch_all_trends(self) -> List[Trend]:
        """Récupère les tendances de tous les connecteurs."""
        tasks = [c.fetch_trends() for c in self.connectors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        trends = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching trends: {result}")
                continue
            trends.extend(result)
        
        # Déduplique par titre (fuzzy matching simple)
        unique_trends = []
        seen_titles = set()
        
        for trend in trends:
            title_lower = trend.title.lower()[:50]
            if title_lower not in seen_titles:
                unique_trends.append(trend)
                seen_titles.add(title_lower)
        
        return unique_trends


# Instances pour les sources
async def create_trend_fetcher(config) -> MultiSourceTrendFetcher:
    """Crée et configure le fetcher de tendances."""
    fetcher = MultiSourceTrendFetcher()
    
    # RSS
    if config.sources.rss_feeds:
        fetcher.add_connector(RSSConnector(config.sources.rss_feeds))
    
    # Reddit
    if config.sources.reddit_enabled:
        fetcher.add_connector(RedditConnector())
    
    # NewsAPI
    if config.sources.newsapi_key:
        fetcher.add_connector(NewsAPIConnector(config.sources.newsapi_key))
    
    # Twitter Trends
    if config.sources.twitter_enabled:
        fetcher.add_connector(TwitterTrendsConnector())
    
    # YouTube Trends
    if config.sources.youtube_enabled:
        fetcher.add_connector(YouTubeTrendsConnector())
    
    return fetcher
