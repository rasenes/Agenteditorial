import json
from pathlib import Path

MEMORY_FILE = Path("backend/memory/performance.json")


def load_perf():
    if not MEMORY_FILE.exists():
        return {}
    return json.loads(MEMORY_FILE.read_text())


def save_perf(data):
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(data, indent=2))


def register_success(mode: str):
    data = load_perf()
    data[mode] = data.get(mode, 0) + 1
    save_perf(data)


def best_modes(limit=3):
    data = load_perf()
    return sorted(data, key=data.get, reverse=True)[:limit]
