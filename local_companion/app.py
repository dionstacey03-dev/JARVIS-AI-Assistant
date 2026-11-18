"""Loopback-only JARVIS bridge to a local Ollama instance.

Run with: uvicorn app:app --host 127.0.0.1 --port 8765
Never bind this service to 0.0.0.0 or expose it through a tunnel.
"""
import hmac
import os
import ipaddress
from typing import Literal

import httpx
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

TOKEN = os.getenv("JARVIS_COMPANION_TOKEN", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
ALLOWED_ORIGINS = [
    value.strip()
    for value in os.getenv(
        "JARVIS_DASHBOARD_ORIGINS",
        "https://jarvis-dashboard-dionstacey03-9459.vercel.app",
    ).split(",")
    if value.strip()
]

app = FastAPI(title="JARVIS Local Companion", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def local_only_and_private_network(request: Request, call_next):
    # Defense in depth: reject any request not originating on this computer.
    peer = request.client.host if request.client else ""
    try:
        if not ipaddress.ip_address(peer).is_loopback:
            raise HTTPException(status_code=403, detail="Local companion accepts loopback connections only.")
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid local connection.")
    response = await call_next(request)
    # Required by browsers that enforce Private Network Access for HTTPS -> loopback.
    if request.headers.get("access-control-request-private-network", "").lower() == "true":
        origin = request.headers.get("origin", "")
        if origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)

class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=12)

def require_token(authorization: str | None):
    if not TOKEN or len(TOKEN) < 32:
        raise HTTPException(status_code=503, detail="Set a companion token of at least 32 characters in the local .env file.")
    supplied = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not hmac.compare_digest(supplied, TOKEN):
        raise HTTPException(status_code=401, detail="Local companion pairing token is invalid.")

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "jarvis-local-companion", "model": OLLAMA_MODEL}

@app.post("/api/chat")
async def chat(payload: ChatRequest, authorization: str | None = Header(default=None)):
    require_token(authorization)
    messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in payload.messages
    ]
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=3.0)) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Ollama returned an error. Check that the selected model is installed.")
        data = response.json()
        reply = data.get("message", {}).get("content")
        if not isinstance(reply, str) or not reply.strip():
            raise HTTPException(status_code=502, detail="Ollama returned an empty response.")
        return {"reply": reply.strip(), "provider": "ollama-local", "model": OLLAMA_MODEL}
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Local Ollama took too long to respond.")
    except (httpx.HTTPError, ValueError, KeyError):
        raise HTTPException(status_code=503, detail="Cannot reach Ollama at the configured local address.")

# Bind only to 127.0.0.1. Do not change this to 0.0.0.0.
