import os
from typing import Literal
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="JARVIS API", version="2.1.0", description="Hosted API for the JARVIS web command center")

origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "*").split(",") if item.strip()]
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
    return {"status": "ok", "service": "jarvis-api", "version": "2.1.0"}

@app.get("/api/status")
async def status():
    configured = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "ok",
        "service": "jarvis-api",
        "assistant": "JARVIS",
        "provider_configured": configured,
        "provider": os.getenv("JARVIS_PROVIDER", "openai-compatible"),
        "model": os.getenv("JARVIS_MODEL", "gpt-4o-mini"),
        "capabilities": {
            "chat": configured,
            "local_desktop": False,
            "voice": False,
            "approval_gated_actions": True
        }
    }

@app.post("/api/chat")
async def chat(payload: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="The AI provider is not configured yet. Add OPENAI_API_KEY in the Vercel backend project's environment variables."
        )

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("JARVIS_MODEL", "gpt-4o-mini")
    system_prompt = (
        "You are JARVIS, a clear, capable and safety-conscious personal AI assistant. "
        "Be practical and concise. You are a hosted web assistant: do not claim to access "
        "the user's computer, files, microphone, local Ollama instance, email, calendar, "
        "or messaging accounts unless a connected tool explicitly provides that capability. "
        "Never claim to have performed an external action. Ask for confirmation before "
        "sensitive actions and explain when an integration is not connected."
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
            # Do not leak provider response bodies or credentials to the browser.
            raise HTTPException(status_code=502, detail="The configured AI provider returned an error. Check its key, model and quota.")
        data = response.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not isinstance(reply, str) or not reply.strip():
            raise HTTPException(status_code=502, detail="The AI provider returned an empty response.")
        return {"reply": reply.strip(), "model": model}
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="The AI provider took too long to respond. Please try again.")
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Could not communicate with the configured AI provider.")

# Vercel's Python runtime discovers this ASGI application.
