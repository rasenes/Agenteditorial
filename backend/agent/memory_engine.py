from __future__ import annotations

import csv
import json
import threading
from pathlib import Path
from typing import Any

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import jaccard_similarity, now_ts
from ..models.tweet import TweetCandidate

logger = get_logger(__name__)


class MemoryEngine:
    def __init__(self, storage_path: str | None = None) -> None:
        self.path = Path(storage_path or SETTINGS.memory.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db: dict[str, Any] = self._default_db()
        self._load_safe()

    def _default_db(self) -> dict[str, Any]:
        return {
            "tweets": [],
            "favorites": [],
            "style_stats": {},
            "theme_heatmap": {},
            "history": [],
            "ab_tests": [],
            "updated_at": now_ts(),
        }

    def _sanitize_db(self, payload: dict[str, Any]) -> dict[str, Any]:
        safe = self._default_db()
        for key in safe.keys():
            if key in payload and isinstance(payload[key], type(safe[key])):
                safe[key] = payload[key]
        safe["updated_at"] = payload.get("updated_at", now_ts())
        return safe

    def _load_safe(self) -> None:
        if not self.path.exists():
            self._save_safe()
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("invalid memory format")
            self._db = self._sanitize_db(payload)
        except Exception as exc:  # noqa: BLE001
            backup = self.path.with_suffix(".corrupted.json")
            self.path.replace(backup)
            logger.error("Memory corrupted. Backup saved to %s (%s)", backup, exc)
            self._db = self._default_db()
            self._save_safe()

    def _save_safe(self) -> None:
        self._db["updated_at"] = now_ts()
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._db, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def register_generation(
        self,
        theme: str,
        trend_text: str,
        tweets: list[TweetCandidate],
        draft_mode: bool,
    ) -> None:
        with self._lock:
            snapshot = {
                "id": f"hist-{int(now_ts() * 1000)}",
                "theme": theme,
                "trend_text": trend_text,
                "draft_mode": draft_mode,
                "created_at": now_ts(),
                "tweet_ids": [tweet.id for tweet in tweets],
                "top_score": max((tweet.score for tweet in tweets), default=0),
            }
            self._db["history"].append(snapshot)
            self._db["history"] = self._db["history"][-SETTINGS.memory.max_history :]

            for tweet in tweets:
                self._register_tweet(tweet)

            self._save_safe()

    def _register_tweet(self, tweet: TweetCandidate) -> None:
        exists = any(jaccard_similarity(tweet.text, row["text"]) >= 0.9 for row in self._db["tweets"][-200:])
        if exists:
            return

        row = tweet.model_dump()
        row["created_at"] = now_ts()
        self._db["tweets"].append(row)
        self._db["tweets"] = self._db["tweets"][-SETTINGS.memory.max_tweets :]

        style = row["style"]
        theme = row["theme"]
        style_stats = self._db["style_stats"].setdefault(style, {"count": 0, "score_sum": 0.0})
        style_stats["count"] += 1
        style_stats["score_sum"] += row["score"]

        heatmap = self._db["theme_heatmap"].setdefault(theme, {"count": 0, "score_sum": 0.0})
        heatmap["count"] += 1
        heatmap["score_sum"] += row["score"]

    def add_favorite(self, tweet_id: str) -> bool:
        with self._lock:
            if tweet_id in self._db["favorites"]:
                return False
            self._db["favorites"].append(tweet_id)
            self._save_safe()
            return True

    def get_similar_texts(self, text: str, threshold: float = 0.82) -> list[str]:
        with self._lock:
            return [
                row["text"]
                for row in self._db["tweets"][-500:]
                if jaccard_similarity(text, row["text"]) >= threshold
            ]

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            tweets = self._db["tweets"]
            avg_score = sum(row.get("score", 0) for row in tweets) / len(tweets) if tweets else 0.0
            return {
                "tweets_count": len(tweets),
                "favorites_count": len(self._db["favorites"]),
                "history_count": len(self._db["history"]),
                "avg_score": round(avg_score, 4),
                "top_styles": self.best_styles(),
                "theme_heatmap": self.theme_heatmap(),
                "updated_at": self._db["updated_at"],
            }

    def list_history(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            return list(reversed(self._db["history"][-limit:]))

    def best_styles(self, top_n: int = 5) -> list[dict[str, Any]]:
        rows = []
        for style, meta in self._db["style_stats"].items():
            count = meta["count"]
            avg = (meta["score_sum"] / count) if count else 0.0
            rows.append({"style": style, "count": count, "avg_score": round(avg, 4)})
        rows.sort(key=lambda r: (r["avg_score"], r["count"]), reverse=True)
        return rows[:top_n]

    def theme_heatmap(self) -> list[dict[str, Any]]:
        rows = []
        for theme, meta in self._db["theme_heatmap"].items():
            count = meta["count"]
            avg = (meta["score_sum"] / count) if count else 0.0
            rows.append({"theme": theme, "count": count, "avg_score": round(avg, 4)})
        rows.sort(key=lambda r: (r["avg_score"], r["count"]), reverse=True)
        return rows

    def register_ab_test(self, payload: dict[str, Any]) -> None:
        with self._lock:
            self._db["ab_tests"].append(payload)
            self._db["ab_tests"] = self._db["ab_tests"][-200:]
            self._save_safe()

    def export_json(self) -> dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._db))

    def export_csv(self, output_path: str) -> str:
        with self._lock:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["id", "text", "theme", "style", "score", "angle", "provider_used", "created_at"],
                )
                writer.writeheader()
                for row in self._db["tweets"]:
                    writer.writerow(
                        {
                            "id": row.get("id", ""),
                            "text": row.get("text", ""),
                            "theme": row.get("theme", ""),
                            "style": row.get("style", ""),
                            "score": row.get("score", 0),
                            "angle": row.get("angle", ""),
                            "provider_used": row.get("provider_used", ""),
                            "created_at": row.get("created_at", 0),
                        }
                    )
            return str(target)

    def clear(self) -> None:
        with self._lock:
            self._db = self._default_db()
            self._save_safe()


memory_engine = MemoryEngine()
