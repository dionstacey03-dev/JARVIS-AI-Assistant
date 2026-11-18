"""Conservative task planning and approval gates for JARVIS."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PlannedAction:
    name: str
    description: str
    requires_approval: bool = True

# Planning is intentionally separate from execution. No arbitrary shell/code tool exists.
SAFE_ACTIONS = {
    "open_application": PlannedAction("open_application", "Open an allow-listed desktop application", False),
    "send_message": PlannedAction("send_message", "Send a message to an external recipient", True),
    "create_calendar_event": PlannedAction("create_calendar_event", "Create or modify a calendar event", True),
    "send_email": PlannedAction("send_email", "Send an email", True),
    "delete_data": PlannedAction("delete_data", "Delete user data", True),
}

def plan_action(name: str) -> PlannedAction:
    try:
        return SAFE_ACTIONS[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported action: {name}") from exc

def authorize(action_name: str, *, user_approved: bool = False) -> bool:
    """Return whether an action may proceed; sensitive actions require explicit approval."""
    action = plan_action(action_name)
    return not action.requires_approval or user_approved
