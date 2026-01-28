import json
from pathlib import Path

MEMORY_PATH = Path("backend/data/memory.json")

def load_memory():
    if not MEMORY_PATH.exists():
        return {}
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory: dict):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def reinforce_mode(mode: str, weight: float = 0.05):
    memory = load_memory()
    memory.setdefault("modes", {})
    memory["modes"][mode] = min(memory["modes"].get(mode, 0.3) + weight, 1.0)
    save_memory(memory)

def reinforce_style(style: str, weight: float = 0.05):
    memory = load_memory()
    memory.setdefault("style", {})
    memory["style"][style] = min(memory["style"].get(style, 0.3) + weight, 1.0)
    save_memory(memory)
