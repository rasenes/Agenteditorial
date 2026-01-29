import json
from pathlib import Path
from typing import Dict, Any

MEMORY_DIR = Path("backend/memory")
MEMORY_FILE = MEMORY_DIR / "memory.json"


def _init_memory() -> Dict[str, Any]:
    return {
        "stats": {},
        "history": [],
        "scores": {}
    }


def load_memory() -> Dict[str, Any]:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not MEMORY_FILE.exists():
        memory = _init_memory()
        save_memory(memory)
        return memory

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = _init_memory()

    # Sécurité structure
    if not isinstance(data, dict):
        data = _init_memory()

    data.setdefault("stats", {})
    data.setdefault("history", [])
    data.setdefault("scores", {})

    return data


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
