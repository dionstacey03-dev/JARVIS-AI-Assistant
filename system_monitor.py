"""Read-only system metrics for the JARVIS dashboard."""
from __future__ import annotations
import platform
import psutil

def get_system_snapshot() -> dict[str, str | int | float | None]:
    battery = psutil.sensors_battery()
    return {
        "platform": f"{platform.system()} {platform.release()}",
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": round(psutil.virtual_memory().used / (1024 ** 3), 1),
        "battery_percent": round(battery.percent) if battery else None,
        "battery_plugged": battery.power_plugged if battery else None,
    }
