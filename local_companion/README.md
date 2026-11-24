# JARVIS Local Companion

This small Windows-side service lets the hosted JARVIS dashboard use Ollama running on the same computer. The browser connects directly to loopback; Vercel never connects to the laptop.

## Security model

- Uvicorn binds only to `127.0.0.1:8765`; do not expose it on your LAN or through a public tunnel.
- Requests must originate from loopback and from an explicitly allowed dashboard origin.
- Chat requests require a random bearer token of at least 32 characters.
- The token stays in the local companion environment and the dashboard's in-memory session state; it is never sent to Vercel.
- The companion only forwards chat messages to the configured local Ollama endpoint. It has no shell, file, browser, or desktop-control endpoints.
- Cloud fallback is an explicit dashboard choice; do not send sensitive local-only content to cloud.

## Windows setup

```powershell
cd local_companion
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `JARVIS_COMPANION_TOKEN` to a long random secret. For example, generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Keep `.env` private. Ensure Ollama is running and the selected model is installed:

```powershell
ollama pull llama3:latest
```

Start the companion from the `local_companion` folder:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app:app --host 127.0.0.1 --port 8765
```

Keep this terminal open while using local fallback. Check `http://127.0.0.1:8765/api/health` on the same computer.

In the dashboard Assistant page, choose **Hybrid (cloud first)** or **Local only**, then paste the same token from `.env` into the Local companion token field. The token is held only in the current browser tab's memory.

## Troubleshooting

- If the browser blocks local requests, confirm the exact dashboard origin is listed in `JARVIS_DASHBOARD_ORIGINS`, restart the companion and reload the page.
- If Ollama is unavailable, start Ollama and confirm `ollama list` includes the configured model.
- Never solve connectivity issues by binding the companion to `0.0.0.0`, disabling token checks, or exposing port 8765 publicly.
