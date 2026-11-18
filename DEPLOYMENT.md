# JARVIS Web Deployment

The original Windows desktop assistant remains intact. The `web/` and `backend/` folders add a browser dashboard and a separately deployable FastAPI service.

## Vercel projects

Create two Vercel projects from this repository:

1. **Dashboard** — Root Directory: `web`; Framework: Vite; Build: `npm run build`; Output: `dist`.
2. **API** — Root Directory: `backend`; Framework: FastAPI / Python.

Deploy each project from the `feature/jarvis-web-dashboard` branch for preview validation, then merge the reviewed pull request and deploy `main) for production.

## Backend environment

Configure these values in the API project's Vercel Settings → Environment Variables:

- `OPENAI_API_KEY` — required provider key; add it directly in Vercel, never commit it.
- `OPENAI_BASE_URL` — optional OpenAI-compatible API base URL; defaults to OpenAI.
- `JARVIS_MODEL` — optional model name; defaults to `gpt-4o-mini`.
- `CORS_ORIGINS` — dashboard origin, for example `https://your-dashboard.vercel.app`.

The backend returns a clear 503 response until an AI provider key is configured. A key is not required for health/status checks.

## Dashboard environment

Set `VITE_API_URL` in the dashboard project to the deployed API origin, for example `https://jarvis-api.vercel.app`. Redeploy the dashboard after setting it.

## Important capability boundary

Vercel hosts the dashboard and stateless API. It cannot directly access the user's Windows desktop, microphone, local Ollama server, files, or local system metrics. Those capabilities require a separately installed and explicitly paired local companion service. Gmail, Calendar and WhatsApp also remain disconnected until their official OAuth/API integrations are implemented and authorized.

## Local checks

Dashboard:

```sh
cd web
npm install
npm run build
```

Backend:

```sh
cd backend
python -m pip install -r requirements.txt
python -c "from api.index import app; print(app.title)"
```
