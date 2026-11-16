"""Online neural text-to-speech playback for JARVIS."""

from __future__ import annotations

import asyncio
import os
import tempfile
import uuid

import edge_tts
import pygame


VOICE = os.getenv("JARVIS_VOICE", "en-US-GuyNeural")


async def _speak_async(text: str) -> None:
    """Synthesize speech to a unique temporary file and play it."""
    temp_path = os.path.join(
        tempfile.gettempdir(),
        f"jarvis-{uuid.uuid4().hex}.mp3",
    )
    try:
        await edge_tts.Communicate(text, VOICE).save(temp_path)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
    finally:
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except pygame.error:
                pass
        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass


def speak(text: str) -> None:
    """Speak text; callers should run this outside the Tkinter UI thread."""
    if not text:
        return
    print(f"JARVIS: {text}")
    try:
        asyncio.run(_speak_async(str(text)))
    except Exception as error:
        # Audio output should never crash the command center.
        print(f"Text-to-speech error: {error}")
