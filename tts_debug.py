import pyttsx3

engine = pyttsx3.init()

print("Driver:", engine)

voices = engine.getProperty("voices")
print(f"Found {len(voices)} voices")

for i, voice in enumerate(voices):
    print(f"\nVoice {i}")
    print("Name :", voice.name)
    print("ID   :", voice.id)

engine.say("Testing one two three.")
engine.runAndWait()

print("Finished")