import json
from pathlib import Path

MEMORY_FILE = Path("backend/data/performance.json")

def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return {}

def save_result(mode: str, score: int):
    memory = load_memory()

    if mode not in memory:
        memory[mode] = {"count": 0, "total_score": 0}

    memory[mode]["count"] += 1
    memory[mode]["total_score"] += score

    MEMORY_FILE.write_text(
        json.dumps(memory, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def get_best_modes(min_count=3):
    memory = load_memory()
    ranked = []

    for mode, data in memory.items():
        if data["count"] >= min_count:
            avg = data["total_score"] / data["count"]
            ranked.append((avg, mode))

    ranked.sort(reverse=True)
    return [m for _, m in ranked]
