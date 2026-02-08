"""
Cache en mémoire avec TTL et limite de taille.
Simple, rapide, et thread-safe.
"""

import time
from typing import Any, Optional, Dict, Callable
from threading import Lock
from functools import wraps

from .logger import get_logger

logger = get_logger(__name__)


class CacheEntry:
    """Entrée du cache avec TTL."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Vérifie si l'entrée a expiré."""
        if self.ttl == 0:
            return False
        return time.time() - self.created_at > self.ttl


class MemoryCache:
    """Cache simple en mémoire thread-safe."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialise le cache.
        
        Args:
            max_size: Nombre max d'entrées
            default_ttl: TTL par défaut (0 = infini)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return None
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Stocke une valeur dans le cache."""
        with self._lock:
            if len(self._cache) >= self.max_size and key not in self._cache:
                # Supprime les entrées expirées d'abord
                self._cleanup()
            
            # Si encore trop grand, supprime les plus anciennes
            if len(self._cache) >= self.max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].created_at
                )
                del self._cache[oldest_key]
            
            ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str) -> None:
        """Supprime une clé du cache."""
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Vide complètement le cache."""
        with self._lock:
            self._cache.clear()
    
    def _cleanup(self) -> None:
        """Supprime les entrées expirées (appelé dans lock)."""
        expired_keys = [
            k for k, v in self._cache.items()
            if v.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def size(self) -> int:
        """Retourne le nombre d'entrées."""
        return len(self._cache)
    
    def stats(self) -> dict:
        """Retourne des stats sur le cache."""
        with self._lock:
            expired = sum(1 for e in self._cache.values() if e.is_expired())
            return {
                "total": len(self._cache),
                "expired": expired,
                "active": len(self._cache) - expired,
                "max_size": self.max_size,
            }


# Instance globale
cache = MemoryCache(max_size=1000, default_ttl=3600)


def cached(ttl: Optional[int] = None):
    """
    Décorateur pour mettre en cache les résultats de fonction.
    
    Args:
        ttl: TTL en secondes (None = default)
    
    Usage:
        @cached(ttl=3600)
        def get_trends():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crée une clé unique
            cache_key = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
            
            # Essaie le cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Calcule et stocke
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
