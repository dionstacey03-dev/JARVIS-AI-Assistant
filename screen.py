"""Screen capture utilities for JARVIS."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageGrab


SCREENSHOT_PATH = Path(__file__).parent / "data" / "screen.png"


def capture_screen() -> str:
    """Capture the current screen and return the image path."""

    SCREENSHOT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = ImageGrab.grab()
    image.save(SCREENSHOT_PATH)

    return str(SCREENSHOT_PATH)