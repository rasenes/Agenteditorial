"""
Orchestrateur principal du pipeline IA editorial.
Coordonne : sources → analyse → génération → scoring → mémoire.
"""

import asyncio
import time
from typing import List, Optional

from ..core.logger import get_logger
from ..core.config import CONFIG
from ..models.tweet import Trend, Tweet, GenerationRequest, GenerationResponse

from .generator import generator
from .scoring import scorer
from .remix_engine import remix_engine
from .memory_engine import memory_engine
from .trend_analyzer import analyzer
from .sources import create_trend_fetcher

logger = get_logger(__name__)


class EditorialOrchestrator:
    """Orchestre le pipeline complet de génération de tweets."""
    
    def __init__(self):
        self.generator = generator
        self.scorer = scorer
        self.remix_engine = remix_engine
        self.memory = memory_engine
        self.analyzer = analyzer
        self.trend_fetcher: Optional[object] = None
    
    async def initialize(self) -> None:
        """Initialise l'orchestrateur (charge les sources, etc.)."""
        try:
            self.trend_fetcher = await create_trend_fetcher(CONFIG)
            logger.info("Editorial Orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
    
    async def fetch_trends(self) -> List[Trend]:
        """Récupère les tendances actuelles."""
        if not self.trend_fetcher:
            logger.warning("Trend fetcher not initialized")
            return []
        
        try:
            trends = await self.trend_fetcher.fetch_all_trends()
            logger.info(f"Fetched {len(trends)} trends")
            
            # Score et analyse
            trends = self.analyzer.score_trends(trends)
            
            return trends
        except Exception as e:
            logger.error(f"Failed to fetch trends: {e}")
            return []
    
    async def generate_for_trend(
        self,
        trend: Trend,
        count: int = 3,
        style: str = "normal",
        create_remixes: bool = False,
    ) -> List[Tweet]:
        """Génère des tweets pour une tendance spécifique."""
        try:
            # Génere
            request = GenerationRequest(
                trend=trend,
                theme=trend.category,
                count=count,
                style=style,
            )
            
            response = await self.generator.generate(request)
            tweets = response.tweets
            
            logger.info(f"Generated {len(tweets)} tweets for {trend.title}")
            
            # Score
            tweets = self.scorer.sort_tweets(tweets)
            
            # Remixes optionnels
            if create_remixes and tweets:
                best_tweet = tweets[0]
                remixes = await self.remix_engine.remix_parallel(best_tweet)
                tweets.extend(remixes)
                logger.info(f"Created {len(remixes)} remixes")
            
            # Stocke en mémoire
            for tweet in tweets[:count]:  # Stocke top K
                self.memory.add_tweet(tweet, tweet.score)
                self.memory.record_style_performance(trend.category, style, tweet.score)
            
            return tweets[:count]
        
        except Exception as e:
            logger.error(f"Generation for trend failed: {e}")
            return []
    
    async def generate_for_trends(
        self,
        trends: List[Trend],
        count_per_trend: int = 2,
        style: str = "normal",
        max_concurrent: int = 3,
    ) -> List[List[Tweet]]:
        """Génère des tweets pour plusieurs tendances."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def _generate_with_limit(trend):
            async with semaphore:
                return await self.generate_for_trend(
                    trend,
                    count=count_per_trend,
                    style=style,
                )
        
        tasks = [_generate_with_limit(trend) for trend in trends]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_tweets = []
        for result in results:
            if isinstance(result, list):
                all_tweets.extend(result)
        
        logger.info(f"Total generated: {len(all_tweets)} tweets")
        return [results[i] for i in range(len(trends))]
    
    async def full_pipeline(
        self,
        num_trends: int = 5,
        tweets_per_trend: int = 3,
        create_remixes: bool = False,
        remix_styles: Optional[List[str]] = None,
    ) -> dict:
        """Exécute le pipeline complet."""
        start_time = time.time()
        
        try:
            # 1. Fetch trends
            logger.info("=== STEP 1: Fetching trends ===")
            trends = await self.fetch_trends()
            trends = trends[:num_trends]
            
            if not trends:
                logger.warning("No trends found")
                return {
                    "status": "error",
                    "message": "No trends found",
                    "execution_time": time.time() - start_time,
                }
            
            # 2. Generate for all trends
            logger.info("=== STEP 2: Generation ===")
            all_results = await self.generate_for_trends(
                trends,
                count_per_trend=tweets_per_trend,
                max_concurrent=3,
            )
            
            # 3. Process remixes if requested
            if create_remixes:
                logger.info("=== STEP 3: Remixing ===")
                all_tweets = []
                for result in all_results:
                    all_tweets.extend(result)
                
                remixed = await self.remix_engine.remix_batch(all_tweets[:5], remix_styles)
                for tweet in remixed[:5]:
                    self.memory.add_tweet(tweet, tweet.score)
            
            # 4. Memory stats
            logger.info("=== STEP 4: Memory ===")
            mem_stats = self.memory.get_memory_stats()
            
            execution_time = time.time() - start_time
            logger.info(f"Pipeline completed in {execution_time:.2f}s")
            
            return {
                "status": "success",
                "trends_analyzed": len(trends),
                "total_tweets_generated": len([t for r in all_results for t in r]),
                "memory_stats": mem_stats,
                "execution_time": execution_time,
            }
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "execution_time": time.time() - start_time,
            }
    
    async def analyze_trend(self, text: str) -> dict:
        """Analyse un texte pour extraire angles viraux."""
        try:
            trend = Trend(title=text, description="")
            angles = self.analyzer.extract_angles(trend)
            
            return {
                "status": "success",
                "angles": angles,
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"status": "error", "message": str(e)}


# Instance globale
orchestrator = EditorialOrchestrator()
