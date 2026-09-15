from pathlib import Path

from PIL import ImageGrab

from vision import analyze_image


SCREENSHOT = Path("data") / "screen.png"


def take_screenshot() -> None:
    """Capture the current Windows screen."""

    SCREENSHOT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = ImageGrab.grab()

    image.save(SCREENSHOT)

    print(f"Screenshot saved to: {SCREENSHOT}")


take_screenshot()


print("\n👁️ JARVIS is analyzing your screen...\n")


answer = analyze_image(
    str(SCREENSHOT),
    "Describe what you can see on this screen. "
    "Mention the main application, visible windows, "
    "and important text if you can read it."
)


print("JARVIS Vision:")
print(answer)