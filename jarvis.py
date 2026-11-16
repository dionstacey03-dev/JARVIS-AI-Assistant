"""Application entry point and command orchestration for JARVIS."""

from __future__ import annotations

import argparse
import time

from commands import execute
from listen import listen
from memory import recall, remember


EXIT_COMMANDS = {"exit", "quit", "goodbye", "shut down jarvis"}


def handle_memory_command(command: str) -> str | None:
    """Handle explicit save and recall requests."""
    normalized = command.casefold().strip()

    if normalized.startswith("my name is "):
        name = command.strip()[len("my name is "):].strip()
        if not name:
            return "I did not catch your name. Please try again."
        remember("name", name)
        return f"Understood. I will remember that your name is {name}."

    if normalized.startswith("remember that "):
        information = command.strip()[len("remember that "):].strip()
        if not information:
            return "What would you like me to remember?"
        remember("last_memory", information)
        return f"Understood. I will remember that {information}."

    if normalized in {"what is my name", "what's my name", "who am i"}:
        name = recall("name")
        return f"Your name is {name}." if name else "I do not know your name yet."

    if normalized in {
        "what did i ask you to remember",
        "what did i tell you to remember",
        "what do you remember",
    }:
        memory = recall("last_memory")
        return (
            f"You asked me to remember that {memory}."
            if memory
            else "You haven't asked me to remember anything yet."
        )

    return None


def process_command(command: str) -> tuple[str, bool]:
    """Process one user request and return (response, should_exit)."""
    text = (command or "").strip()
    if not text:
        return "Please enter a request.", False

    normalized = text.casefold()
    if normalized in EXIT_COMMANDS:
        return "Goodbye. JARVIS is shutting down.", True

    try:
        memory_response = handle_memory_command(text)
        if memory_response is not None:
            return memory_response, False

        command_response = execute(text)
        if command_response is not None:
            return command_response, False

        # Import lazily so basic commands remain available if Ollama
        # has not yet been installed or configured.
        from ai import ask_ai

        return ask_ai(text), False
    except Exception as error:
        print(f"Command processing error: {error}")
        return (
            "I ran into a problem while processing that request. "
            "Please check the JARVIS setup and try again.",
            False,
        )


def run_voice_mode() -> None:
    """Run the hands-free wake-word interaction loop."""
    from voice import speak
    from wakeword import wait_for_wake_word

    print("JARVIS voice mode is ready. Say 'Hey Jarvis' to begin.")
    while True:
        try:
            wait_for_wake_word()
            speak("I'm listening.")
            spoken = listen()
            if not spoken:
                speak("I didn't catch that. Please try again.")
                continue

            response, should_exit = process_command(spoken)
            speak(response)
            if should_exit:
                break
            time.sleep(0.2)
        except KeyboardInterrupt:
            print("\nJARVIS voice mode stopped.")
            break
        except Exception as error:
            print(f"Voice mode error: {error}")
            time.sleep(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="JARVIS desktop voice assistant")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Start hands-free wake-word mode instead of the desktop interface",
    )
    args = parser.parse_args()

    if args.voice:
        run_voice_mode()
    else:
        from ui import launch

        launch()


if __name__ == "__main__":
    main()
