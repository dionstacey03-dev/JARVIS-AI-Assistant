"""Bounded, local-only conversation history for JARVIS."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HISTORY_FILE = Path(__file__).parent / "data" / "conversation.json"
MAX_TURNS = 40
MAX_CHARS = 4000

def load_history() -> list[dict[str, str]]:
    try:
        data: Any = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return [
            {"role": item["role"], "content": item["content"]}
            for item in data[-MAX_TURNS:]
            if isinstance(item, dict)
            and item.get("role") in {"user", "assistant"}
            and isinstance(item.get("content"), str)
        ]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return []

def add_turn(role: str, content: str) -> None:
    if role not in {"user", "assistant"}:
        raise ValueError("role must be user or assistant")
    if not isinstance(content, str) or not content.strip():
        return
    history = load_history()
    history.append({"role": role, "content": content.strip()[:MAX_CHARS]})
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = HISTORY_FILE.with_suffix(".tmp")
    try:
        temp.write_text(json.dumps(history[-MAX_TURNS:], ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(HISTORY_FILE)
    finally:
        if temp.exists():
            temp.unlink()

def clear_history() -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text("[]\n", encoding="utf-8")
