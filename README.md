# JARVIS — Desktop AI Voice Assistant

JARVIS is a local-first Windows desktop assistant built with Python. It combines a Tkinter command center, voice input, wake-word activation, desktop actions, persistent local memory, screen capture, Ollama-powered answers, and neural text-to-speech.

## Features

- Desktop command center with typed requests, activity history, quick actions, and a live clock
- Optional hands-free wake-word mode ("Hey Jarvis", "Okay Jarvis")
- Common Windows application and website launching
- Google and YouTube search shortcuts
- Local JSON memory for explicit remember/recall commands
- Optional local AI responses through Ollama
- Screen capture and image analysis with an Ollama vision model
- Neural text-to-speech through Edge TTS

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- A working microphone for voice features
- Internet access for Google speech recognition and Edge TTS
- [Ollama](https://ollama.com) for AI answers and screen-image analysis

Tkinter is included with most standard Windows Python installations. PyAudio may require a compatible prebuilt wheel on some Windows/Python combinations.

## Installation

Open PowerShell in the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install the default local language model:

```powershell
ollama pull llama3
```

For screen-image analysis, also install the default vision model:

```powershell
ollama pull llava
```

Make sure the Ollama application/service is running before asking open-ended AI questions.

## Run JARVIS

Start the desktop command center:

```powershell
python jarvis.py
```

Start hands-free wake-word mode:

```powershell
python jarvis.py --voice
```

## Configuration

Set a different installed Ollama language model in PowerShell:

```powershell
$env:JARVIS_MODEL = "llama3.2"
```

Set a different vision model:

```powershell
$env:JARVIS_VISION_MODEL = "llava"
```

Set a different Edge TTS voice:

```powershell
$env:JARVIS_VOICE = "en-US-GuyNeural"
```

## Example commands

- "Open YouTube", "Open Calculator", "Open File Explorer"
- "Search Google for Python tutorials"
- "Search YouTube for Python programming"
- "What time is it?", "What is the date?"
- "My name is [name]", "What is my name?"
- "Remember that [information]", "What do you remember?"
- "What is on my screen?"
- "Goodbye"

## Privacy and limitations

- Explicit memories are stored locally in `data/memory.json`; this folder is excluded from Git.
- Speech recognition uses Google's online recognition service and requires internet access.
- Edge TTS sends text to Microsoft's online speech service.
- Ollama language and vision inference run locally after the models are downloaded.
- Screen analysis captures the current desktop and sends the image to the configured local Ollama vision model. Use this only when appropriate for the content visible on screen.

## Development checks

Run the test suite with:

```powershell
python -m unittest discover -s tests -v
```

## Manual Windows hardware validation

Automated CI deliberately avoids accessing a real microphone, speaker, desktop session, or local Ollama service. Before treating a machine-specific setup as fully verified, run these checks on the target Windows PC:

1. Activate the virtual environment and run `python jarvis.py`; confirm the command-center window opens.
2. Submit `what time is it` and `open calculator`; confirm the response and application launch.
3. Toggle Voice responses off and on; confirm typed requests still work in both states.
4. Click Listen, speak a short sentence, and confirm the recognized request appears in the activity log.
5. Submit `my name is Test User`, then `what is my name`; confirm the saved value is recalled. Remove the test entry from `data/memory.json` afterward if desired.
6. Start `python jarvis.py --voice`, say `Hey Jarvis`, and confirm it listens for a command after the wake phrase.
7. With Ollama running and the configured model pulled, ask a general question; then stop Ollama and confirm JARVIS displays a helpful fallback instead of crashing.
8. Ask `what is on my screen` with Ollama and the configured vision model running; confirm the image analysis responds as expected.
9. Close the desktop window while idle and confirm the process exits cleanly.

Screen capture and cloud speech/TTS services can expose on-screen or spoken content to local or external services as described in the Privacy section above. Only run those checks when appropriate.
