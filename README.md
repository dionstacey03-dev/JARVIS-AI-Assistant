# JARVIS Voice Assistant

A polished local Windows voice assistant with wake-word activation, common desktop commands, lightweight persistent memory, text-to-speech, and optional Ollama-powered answers.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Install and start [Ollama](https://ollama.com), then pull the default model: `ollama pull llama3`
4. Start the desktop command center: `python jarvis.py`

Use `python jarvis.py --voice` for the original hands-free wake-word mode.

Set `JARVIS_MODEL` to use another installed Ollama model. For example in PowerShell: `$env:JARVIS_MODEL = "llama3.2"`.

## Voice commands

- Say **"Hey Jarvis"**, then ask a question or give a command.
- "Open YouTube", "Open Calculator", "Open File Explorer"
- "Search Google for [topic]" or "Search YouTube for [topic]"
- "What time is it?"
- "My name is [name]" and "What is my name?"
- "Goodbye" to exit

## Desktop interface

The command center supports typed requests, one-click microphone input, live activity history, quick actions, a system clock, and a voice-response toggle. It uses Tkinter, included with standard Windows Python installations.

## Notes

Speech recognition uses Google's online recognition service, so an internet connection is needed for transcription. Ollama runs locally but must be running before open-ended AI requests can be answered.
