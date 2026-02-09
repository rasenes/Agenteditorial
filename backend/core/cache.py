from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(self, max_size: int = 1024, ttl_seconds: int = 300) -> None:
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._data: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            if entry.expires_at < time.time():
                self._data.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        with self._lock:
            if len(self._data) >= self.max_size and key not in self._data:
                # Eviction policy: remove oldest expiry first.
                oldest_key = min(self._data.keys(), key=lambda k: self._data[k].expires_at)
                self._data.pop(oldest_key, None)
            self._data[key] = CacheEntry(value=value, expires_at=time.time() + ttl)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def stats(self) -> dict[str, int]:
        with self._lock:
            now = time.time()
            alive = sum(1 for entry in self._data.values() if entry.expires_at >= now)
            return {
                "size": len(self._data),
                "alive": alive,
                "expired": len(self._data) - alive,
                "max_size": self.max_size,
            }


cache = TTLCache()
