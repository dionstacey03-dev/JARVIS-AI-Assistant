"""Vision capabilities for JARVIS using Ollama."""

from __future__ import annotations

import os

from ollama import chat


VISION_MODEL = os.getenv("JARVIS_VISION_MODEL", "llava")


def analyze_image(image_path: str, question: str) -> str:
    """Analyze an image using the Ollama vision model."""

    try:
        response = chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "images": [image_path],
                }
            ],
        )

        answer = response["message"]["content"].strip()

        return answer or "I couldn't determine what is in the image."

    except Exception as error:
        print(f"Vision error: {error}")

        return (
            "I couldn't analyze the image. "
            f"Please make sure the {VISION_MODEL} model is installed "
            "and Ollama is running."
        )