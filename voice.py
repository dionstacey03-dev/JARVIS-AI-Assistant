import asyncio
import os
import tempfile

import edge_tts
import pygame

VOICE = "en-US-GuyNeural"

pygame.mixer.init()


async def _speak_async(text):
    temp_file = os.path.join(tempfile.gettempdir(), "jarvis_voice.mp3")

    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(temp_file)

    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.music.unload()

    try:
        os.remove(temp_file)
    except PermissionError:
        pass


def speak(text):
    if not text:
        return

    print(f"Jarvis: {text}")

    asyncio.run(_speak_async(str(text)))
