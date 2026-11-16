"""Persistent structured memory store for JARVIS."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


MEMORY_FILE = Path(__file__).parent / "data" / "memory.json"


def load_memory() -> dict[str, Any]:
    """Load saved memories; return an empty store for missing or invalid data."""
    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_memory(memory: dict[str, Any]) -> None:
    """Atomically persist memories to avoid partially-written JSON files."""
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=MEMORY_FILE.parent,
            prefix=".memory-",
            suffix=".tmp",
            delete=False,
        ) as file:
            json.dump(memory, file, indent=2, ensure_ascii=False, sort_keys=True)
            file.write("\n")
            temp_path = file.name
        os.replace(temp_path, MEMORY_FILE)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def remember(key: str, value: Any) -> None:
    """Save or update one memory."""
    if not key or not key.strip():
        raise ValueError("Memory key cannot be empty")
    memory = load_memory()
    memory[key] = value
    save_memory(memory)


def recall(key: str) -> Any | None:
    """Retrieve one memory."""
    return load_memory().get(key)


def forget(key: str) -> bool:
    """Delete one memory."""
    memory = load_memory()
    if key not in memory:
        return False
    del memory[key]
    save_memory(memory)
    return True


def get_all_memories() -> dict[str, Any]:
    """Return all saved memories."""
    return load_memory()
