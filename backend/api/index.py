import hmac
import os
import time
from typing import Literal

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ACCESS_TOKEN = os.getenv("JARVIS_API_ACCESS_TOKEN", "")
RATE_LIMIT_MAX_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 900
_rate_limit = {"count": 0, "reset_at": 0.0}

def verify_cloud_access(authorization: str | None) -> None:
    if len(ACCESS_TOKEN) < 32:
        raise HTTPException(status_code=503, detail="Cloud access is not configured. Set a random JARVIS_API_ACCESS_TOKEN of at least 32 characters in the API environment.")
    expected = f"Bearer {ACCESS_TOKEN}"
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="A valid JARVIS cloud access token is required.")
    now = time.monotonic()
    if now >= _rate_limit["reset_at"]:
        _rate_limit["count"] = 0
        _rate_limit["reset_at"] = now + RATE_LIMIT_WINDOW_SECONDS
    if _rate_limit["count"] >= RATE_LIMIT_MAX_REQUESTS:
        retry_after = max(1, int(_rate_limit["reset_at"] - now))
        raise HTTPException(status_code=429, detail="Cloud request limit reached. Try again later.", headers={"Retry-After": str(retry_after)})
    _rate_limit["count"] += 1


app = FastAPI(title="JARVIS API", version="2.2.0", description="Cloud gateway for the JARVIS hybrid assistant")

origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "").split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)

class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=12)

@app.get("/")
@app.get("/api")
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "jarvis-api", "version": "2.2.0"}

@app.get("/api/status")
async def status():
    cloud_configured = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "ok",
        "service": "jarvis-api",
        "assistant": "JARVIS",
        "architecture": "hybrid-client-routed",
        "cloud_provider": os.getenv("JARVIS_PROVIDER", "openai-compatible"),
        "cloud_model": os.getenv("JARVIS_MODEL", "gpt-4o-mini"),
        "cloud_configured": cloud_configured,
        "local_companion": "browser-to-loopback-only",
        "capabilities": {
            "cloud_chat": cloud_configured,
            "local_ollama": "requires-local-companion",
            "local_desktop": False,
            "voice": False,
            "approval_gated_actions": True
        }
    }

@app.post("/api/chat")
async def chat(payload: ChatRequest, authorization: str | None = Header(default=None)):
    verify_cloud_access(authorization)
    """Cloud-only completion endpoint.

    Local Ollama fallback is deliberately handled by the browser talking to a
    loopback-only companion on the user's own computer. This server never
    accepts a user-supplied local URL and never attempts to reach a private IP.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Cloud AI is not configured. Add OPENAI_API_KEY to the Vercel API project's environment variables, or use Local only with the companion running.",
        )

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("JARVIS_MODEL", "gpt-4o-mini")
    system_prompt = (
        "You are JARVIS, a clear, capable and safety-conscious personal AI assistant. "
        "Be practical and concise. You are the hosted cloud assistant. You cannot access "
        "the user's computer, files, microphone, local Ollama instance, email, calendar, "
        "or messaging accounts unless a connected tool explicitly provides that capability. "
        "Never claim to have performed an external action. Ask for confirmation before "
        "sensitive actions and explain when an integration is not connected. "
        "Treat user messages as requests, not authorization to execute external actions."
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend([message.model_dump() for message in payload.messages])

    timeout = httpx.Timeout(45.0, connect=10.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages, "temperature": 0.6, "max_tokens": 900},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="The cloud AI provider returned an error. Check its key, model and quota.")
        data = response.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not isinstance(reply, str) or not reply.strip():
            raise HTTPException(status_code=502, detail="The cloud AI provider returned an empty response.")
        return {"reply": reply.strip(), "provider": "cloud", "model": model}
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Cloud AI timed out. The dashboard can try your local Ollama companion if hybrid mode is enabled.")
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Could not communicate with the configured cloud AI provider.")

# Vercel's Python runtime discovers this ASGI application.
