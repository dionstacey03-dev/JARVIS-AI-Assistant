import speech_recognition as sr

recognizer = sr.Recognizer()

# Microphone sensitivity
recognizer.energy_threshold = 250
recognizer.dynamic_energy_threshold = True

# How long Jarvis waits after you stop speaking
recognizer.pause_threshold = 0.8


def listen():
    """Listen to the microphone and return the recognized speech."""

    with sr.Microphone() as source:
        print("🎤 Listening...")

        try:
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=10
            )

            print("🧠 Recognizing...")

            text = recognizer.recognize_google(audio)

            print(f"You: {text}")

            return text.lower()

        except sr.WaitTimeoutError:
            print("⏰ No speech detected.")
            return None

        except sr.UnknownValueError:
            print("🤷 I couldn't understand that.")
            return None

        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            return None

        except Exception as e:
            print(f"❌ Microphone error: {e}")
            return None