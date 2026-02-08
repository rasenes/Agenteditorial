"""
Moteur de mémoire intelligente.
Stocke les tweets performants et évite la redondance.
"""

import json
import hashlib
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
from threading import Lock

from ..core.logger import get_logger
from ..core.config import CONFIG
from ..models.tweet import Tweet

logger = get_logger(__name__)


class MemoryEngine:
    """Gère une mémoire persistante des tweets et tendances."""
    
    def __init__(self, path: Optional[str] = None):
        self.path = Path(path or CONFIG.memory.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._cache: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Charge la mémoire depuis le fichier."""
        try:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded memory from {self.path}")
            else:
                self._cache = {
                    "tweets": [],
                    "trends": [],
                    "styles": {},
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "version": "1.0",
                    }
                }
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self._cache = {
                "tweets": [],
                "trends": [],
                "styles": {},
                "metadata": {"created_at": datetime.now().isoformat()},
            }
    
    def _save(self) -> None:
        """Sauvegarde la mémoire dans le fichier."""
        try:
            with self._lock:
                # Évite de dépasser max_size
                tweets = self._cache.get("tweets", [])
                if len(tweets) > CONFIG.memory.max_size:
                    # Garde les plus récents
                    tweets = tweets[-CONFIG.memory.max_size:]
                    self._cache["tweets"] = tweets
                
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump(self._cache, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def add_tweet(self, tweet: Tweet, score: float, engagement: int = 0) -> None:
        """Ajoute un tweet à la mémoire."""
        entry = {
            "content": tweet.content,
            "score": score,
            "theme": tweet.theme,
            "language": tweet.language,
            "engagement": engagement,
            "created_at": datetime.now().isoformat(),
            "metadata": tweet.metadata or {},
        }
        
        with self._lock:
            tweets = self._cache.get("tweets", [])
            
            # Évite les doublons (fuzzy hash)
            content_hash = self._hash_content(tweet.content)
            if not any(self._hash_content(t["content"]) == content_hash for t in tweets[-100:]):
                tweets.append(entry)
                self._cache["tweets"] = tweets
                self._save()
    
    def add_trend(self, title: str, category: str, generated_count: int = 0) -> None:
        """Ajoute une tendance à la mémoire."""
        entry = {
            "title": title,
            "category": category,
            "generated_count": generated_count,
            "created_at": datetime.now().isoformat(),
        }
        
        with self._lock:
            trends = self._cache.get("trends", [])
            trends.append(entry)
            self._cache["trends"] = trends
            self._save()
    
    def get_trending_styles(self, theme: str = "general", top_k: int = 5) -> List[str]:
        """Récupère les styles les plus efficaces pour un thème."""
        with self._lock:
            styles = self._cache.get("styles", {})
            theme_styles = styles.get(theme, {})
            
            sorted_styles = sorted(
                theme_styles.items(),
                key=lambda x: x[1].get("avg_score", 0),
                reverse=True
            )
            
            return [s[0] for s in sorted_styles[:top_k]]
    
    def record_style_performance(self, theme: str, style: str, score: float) -> None:
        """Enregistre la performance d'un style."""
        with self._lock:
            styles = self._cache.get("styles", {})
            if theme not in styles:
                styles[theme] = {}
            
            if style not in styles[theme]:
                styles[theme][style] = {"count": 0, "total_score": 0.0}
            
            styles[theme][style]["count"] += 1
            styles[theme][style]["total_score"] += score
            styles[theme][style]["avg_score"] = (
                styles[theme][style]["total_score"] / styles[theme][style]["count"]
            )
            
            self._cache["styles"] = styles
            self._save()
    
    def get_similar_tweets(self, text: str, threshold: float = 0.8) -> List[str]:
        """Trouve des tweets similaires dans la mémoire."""
        with self._lock:
            tweets = self._cache.get("tweets", [])
            similar = []
            
            for tweet in tweets[-500:]:  # Cherche dans les 500 derniers
                similarity = self._similarity_score(text, tweet["content"])
                if similarity >= threshold:
                    similar.append(tweet["content"])
            
            return similar
    
    def get_similar_themes(self, theme: str) -> List[str]:
        """Trouve des tendances similaires stockées."""
        with self._lock:
            trends = self._cache.get("trends", [])
            similar_themes = set()
            
            for trend in trends:
                if trend.get("category") == theme:
                    similar_themes.add(trend["title"])
            
            return list(similar_themes)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Retourne des stats sur la mémoire."""
        with self._lock:
            tweets = self._cache.get("tweets", [])
            trends = self._cache.get("trends", [])
            
            avg_score = sum(t.get("score", 0) for t in tweets) / len(tweets) if tweets else 0
            
            return {
                "tweets_count": len(tweets),
                "trends_count": len(trends),
                "avg_tweet_score": avg_score,
                "created_at": self._cache.get("metadata", {}).get("created_at"),
            }
    
    @staticmethod
    def _hash_content(text: str) -> str:
        """Hash simple d'un contenu."""
        # Normalise et hash
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    @staticmethod
    def _similarity_score(text1: str, text2: str) -> float:
        """Calcule une similarité simple entre deux textes."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def clear(self) -> None:
        """Vide la mémoire."""
        with self._lock:
            self._cache = {
                "tweets": [],
                "trends": [],
                "styles": {},
                "metadata": {"created_at": datetime.now().isoformat()},
            }
            self._save()


# Instance globale
memory_engine = MemoryEngine()
