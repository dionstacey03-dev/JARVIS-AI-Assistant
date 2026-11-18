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


## JARVIS V2 foundations

The V2 upgrade adds bounded local conversation history, a conservative action planner,
integration readiness reporting, an opt-in WhatsApp Cloud API sender, and read-only
system metrics.

### Local conversation history

Conversation turns are stored in `data/conversation.json` (ignored by Git), capped at
40 turns and 4,000 characters per turn. This file is local user data; do not commit it.

### Action approval and safety

`orchestrator.py` separates planning from execution. External communication,
calendar changes, email sending, and deletion are approval-gated. Unknown actions are
rejected; there is no arbitrary shell execution tool exposed by the planner.

### Optional integrations

- WhatsApp: configure `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, and optionally
  `WHATSAPP_API_VERSION`. Sending requires `user_approved=True` at the call site.
- Gmail and Google Calendar: set `GOOGLE_OAUTH_CLIENT_ID` and
  `GOOGLE_OAUTH_CLIENT_SECRET` to indicate OAuth app configuration. This release does
  not yet perform OAuth login or access Gmail/Calendar data; a consent-based OAuth
  adapter remains a follow-up integration task.
- No secrets belong in source files or committed configuration.

### System metrics

Use `system_monitor.get_system_snapshot()` for read-only CPU, memory, platform, and
battery telemetry. Metrics are local and are not transmitted.

### V2 tests

Run:

```powershell
python -m unittest discover -s tests -v
```

