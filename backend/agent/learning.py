import json
from pathlib import Path
from datetime import datetime

MEMORY_PATH = Path("memory/memory.json")

def load_memory():
    if not MEMORY_PATH.exists():
        return []
    try:
        return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_entry(data: dict):
    memory = load_memory()
    data["timestamp"] = datetime.utcnow().isoformat()
    memory.append(data)
    MEMORY_PATH.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
