"""Persistent structured memory store for JARVIS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MEMORY_FILE = Path(__file__).parent / "data" / "memory.json"


def load_memory() -> dict[str, Any]:
    """Load all saved memories."""

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_memory(memory: dict[str, Any]) -> None:
    """Save memories to disk."""

    MEMORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )


def remember(key: str, value: Any) -> None:
    """Save or update one memory."""

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