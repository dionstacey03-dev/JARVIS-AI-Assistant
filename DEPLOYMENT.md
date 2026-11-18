# JARVIS Hybrid Web Deployment

The original Windows desktop application and its V2 modules remain in place. The `web/` and `backend/` folders provide a hosted command center and cloud API. The `local_companion/` folder adds an optional, loopback-only bridge to Ollama on the user's Windows computer.

## Architecture

- **Vercel dashboard:** React + Vite interface.
- **Vercel API:** Cloud AI gateway; stores the cloud provider key only as a Vercel environment variable.
- **Local companion:** Runs on the user's PC, binds only to `127.0.0.1:8765`, and talks to Ollama at `127.0.0.1:11434`.
- **Routing:** Hybrid mode tries the cloud API first. If it is unavailable, the browser can send the conversation directly to the local companion. Local-only and cloud-only modes are also available.
- **Security:** The hosted API never receives the local companion token and never connects to a user-supplied private URL. The companion requires a long bearer token, accepts only loopback connections and allows only explicitly configured dashboard origins. It exposes chat only, not shell, file, or desktop-control operations.

## Vercel projects

Keep the two existing Vercel projects connected to this repository:

1. **Dashboard** — Root Directory: `web`; Framework: Vite; Build: `npm run build`; Output: `dist`.
2. **API** — Root Directory: `backend`; Framework: FastAPI / Python; Function region: Singapore (`sin1`).

Use the `feature/jarvis-web-dashboard` branch for preview validation. After review and merge, production deployments should come from `main`. Do not promote the feature-branch preview to production.

## Backend environment

Configure these in the API project's Vercel Settings → Environment Variables:

- `OPENAI_API_KEY` — required for cloud AI. Add it directly in Vercel; never commit it or paste it into chat.
- `OPENAI_BASE_URL` — optional OpenAI-compatible API base URL; defaults to OpenAI.
- `JARVIS_MODEL` — optional model name; defaults to `gpt-4o-mini`.
- `CORS_ORIGINS` — exact dashboard origin, for example `https://jarvis-dashboard-dionstacey03-9459.vercel.app`.

The API health/status routes work without a provider key. Cloud chat returns a clear setup error until the key is configured.

## Dashboard environment

Set `VITE_API_URL` in the dashboard Vercel project to the API deployment origin, for example `https://jarvis-api-dionstacey03-9459.vercel.app`. This is a public API base URL, not a secret.

## Windows local companion setup

See [local_companion/README.md](local_companion/README.md). In short:

1. Install Ollama and ensure the configured model is available (`ollama pull llama3:latest`).
2. Install Python dependencies from `local_companion/requirements.txt`.
3. Copy `.env.example` to `.env` and set a random token with at least 32 characters.
4. Set `JARVIS_DASHBOARD_ORIGINS` to the exact production dashboard origin.
5. Start the service from the `local_companion` directory with:

```powershell
uvicorn app:app --host 127.0.0.1 --port 8765
```

6. In the dashboard Assistant page, select Hybrid or Local only and paste the same token into the Local token field.

Never bind the companion to `0.0.0.0`, expose port 8765 through a tunnel, or disable token/origin checks. The local token is used only by the browser-to-loopback request and is not sent to Vercel.

## Capability boundaries

The hosted dashboard does not automatically gain access to the user's Windows screen, files, microphone, or system telemetry. The local companion in this phase provides authenticated local Ollama chat only. Desktop monitoring, voice, Gmail, Calendar and WhatsApp require separate integrations and explicit authorization; they must not be displayed as connected until implemented and tested.

## Local checks

Dashboard:

```sh
cd web
npm install
npm run build
```

Hosted API:

```sh
cd backend
python -m pip install -r requirements.txt
python -c "from api.index import app; print(app.title)"
```

Local companion:

```sh
cd local_companion
python -m pip install -r requirements.txt
python -c "from app import app; print(app.title)"
```
