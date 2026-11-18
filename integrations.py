"""Optional external integrations with explicit configuration and approval gates.

This module never stores credentials in source code. Gmail and Calendar are reported
as configuration-ready only; their OAuth adapters are intentionally opt-in follow-up
work rather than silently using a user's account.
"""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request

def integration_status() -> dict[str, str]:
    return {
        "ollama": "configured" if os.getenv("OLLAMA_HOST") or _ollama_available_hint() else "local service expected",
        "gmail": "credentials configured" if os.getenv("GOOGLE_OAUTH_CLIENT_ID") and os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") else "not connected",
        "calendar": "credentials configured" if os.getenv("GOOGLE_OAUTH_CLIENT_ID") and os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") else "not connected",
        "whatsapp": "configured" if all(os.getenv(k) for k in ("WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID")) else "not connected",
    }

def _ollama_available_hint() -> bool:
    return bool(os.getenv("OLLAMA_MODEL") or os.getenv("JARVIS_MODEL"))

def send_whatsapp_message(to: str, message: str, *, user_approved: bool = False) -> dict[str, str]:
    """Send via Meta WhatsApp Cloud API only after explicit approval."""
    if not user_approved:
        raise PermissionError("Explicit user approval is required before sending a WhatsApp message.")
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    version = os.getenv("WHATSAPP_API_VERSION", "v23.0")
    if not token or not phone_id:
        raise RuntimeError("Configure WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID first.")
    if not to.strip() or not message.strip():
        raise ValueError("Recipient and message are required.")
    payload = json.dumps({
        "messaging_product": "whatsapp", "to": to,
        "type": "text", "text": {"body": message}
    }).encode("utf-8")
    request = urllib.request.Request(
        f"https://graph.facebook.com/{version}/{phone_id}/messages",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        return {"status": "sent", "message_id": data.get("messages", [{}])[0].get("id", "")}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"WhatsApp API returned HTTP {exc.code}: {detail}") from exc
