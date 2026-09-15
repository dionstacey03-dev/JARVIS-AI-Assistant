"""Wake-word detection for JARVIS."""

import speech_recognition as sr


WAKE_PHRASES = (
    "hey jarvis",
    "okay jarvis",
    "ok jarvis",
)

recognizer = sr.Recognizer()

recognizer.energy_threshold = 250
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8


def wait_for_wake_word() -> None:
    """Wait until a supported wake phrase is recognized."""

    print("👂 Waiting for wake word...")

    with sr.Microphone() as source:

        # Calibrate microphone once
        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        while True:
            try:
                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=4
                )

                print("🧠 Checking...")

                heard = recognizer.recognize_google(audio).casefold()

                print(f"Heard: {heard}")

                if any(
                    phrase in heard
                    for phrase in WAKE_PHRASES
                ):
                    print("🤖 Wake word detected!")
                    return

            except sr.WaitTimeoutError:
                continue

            except sr.UnknownValueError:
                print("❓ Didn't understand.")
                continue

            except sr.RequestError as error:
                print("❌ Speech recognition service unavailable.")
                raise RuntimeError(
                    "Speech recognition service is unavailable."
                ) from error
