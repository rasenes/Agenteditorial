# backend/agent/memory_engine.py
import json
from pathlib import Path
from typing import Any, Dict

MEMORY_DIR = Path("memory")
MEMORY_FILE = MEMORY_DIR / "memory.json"


def _default_memory() -> Dict[str, Any]:
    return {"history": [], "stats": {}}


def _normalize_memory(data: Any) -> Dict[str, Any]:
    """Normalize legacy memory formats to a dict with history/stats."""
    if isinstance(data, dict):
        data.setdefault("history", [])
        data.setdefault("stats", {})
        if not isinstance(data["history"], list):
            data["history"] = []
        if not isinstance(data["stats"], dict):
            data["stats"] = {}
        return data

    if isinstance(data, list):
        memory = _default_memory()
        for entry in data:
            if not isinstance(entry, dict):
                continue
            mode = str(entry.get("mechanic") or entry.get("mode") or "legacy")
            tweets = entry.get("tweets") or []
            if not isinstance(tweets, list):
                continue
            for tweet in tweets:
                if isinstance(tweet, str) and tweet.strip():
                    memory["history"].append({"mode": mode, "tweet": tweet.strip()})
                    memory["stats"][mode] = memory["stats"].get(mode, 0) + 1
        return memory

    return _default_memory()


def load_memory() -> Dict[str, Any]:
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return _default_memory()
    else:
        return _default_memory()

    return _normalize_memory(data)


def save_memory(memory: Dict[str, Any]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def register_success(mode: str, tweet: str) -> None:
    memory = load_memory()

    stats = memory["stats"]
    stats[mode] = stats.get(mode, 0) + 1

    memory["history"].append({
        "mode": mode,
        "tweet": tweet
    })

    save_memory(memory)
