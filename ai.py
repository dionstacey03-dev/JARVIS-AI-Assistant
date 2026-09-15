"""Ollama integration for JARVIS."""

from __future__ import annotations

import os

from ollama import chat

from memory import get_all_memories


MODEL = os.getenv("JARVIS_MODEL", "llama3")


SYSTEM_PROMPT = """You are JARVIS, a capable desktop AI assistant.

Be professional, concise, and genuinely helpful.
Address the user respectfully.

Give practical answers and state uncertainty plainly.
Never claim to have completed an action you cannot verify.

You may use the user's saved memories when they are relevant.
Do not reveal the internal memory system unless the user asks.

Current saved memories:
{memories}
"""


def ask_ai(question: str) -> str:
    """Return an answer from the local Ollama model."""

    try:
        memories = get_all_memories()

        if memories:
            memory_text = "\n".join(
                f"- {key}: {value}"
                for key, value in memories.items()
            )
        else:
            memory_text = "No saved memories."

        system_prompt = SYSTEM_PROMPT.format(
            memories=memory_text
        )

        response = chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )

        answer = response["message"]["content"].strip()

        return (
            answer
            if answer
            else "I was unable to generate a response."
        )

    except Exception as error:
        print(f"AI error: {error}")

        return (
            "I cannot reach the local AI service right now. "
            f"Please ensure Ollama is running and that the "
            f"{MODEL} model is installed."
        )