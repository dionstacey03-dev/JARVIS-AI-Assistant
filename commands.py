"""Built-in desktop, web, and screen commands for JARVIS."""

from __future__ import annotations

import datetime as dt
import platform
import subprocess
import urllib.parse
import webbrowser

import psutil

from screen import capture_screen
from vision import analyze_image


# --------------------------------------------------
# Websites
# --------------------------------------------------

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
}


# --------------------------------------------------
# Windows Applications
# --------------------------------------------------

APPLICATIONS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "command prompt": "cmd.exe",
    "file explorer": "explorer.exe",
}


# --------------------------------------------------
# Application Launcher
# --------------------------------------------------

def _open_application(application: str) -> None:
    """Launch a Windows application."""

    subprocess.Popen(
        [application],
        shell=False,
    )


# --------------------------------------------------
# Web Search
# --------------------------------------------------

def _search(
    command: str,
    prefix: str,
    template: str,
    service: str,
) -> str | None:
    """Search a web service."""

    if not command.startswith(prefix):
        return None

    query = command.removeprefix(prefix).strip()

    if not query:
        return (
            f"Please tell me what you would like "
            f"to search for on {service}."
        )

    encoded_query = urllib.parse.quote_plus(query)

    webbrowser.open(
        template.format(query=encoded_query)
    )

    return f"Searching {service} for {query}."


# --------------------------------------------------
# System Information
# --------------------------------------------------

def _system_info() -> str:
    """Return basic computer information."""

    system = platform.system()
    version = platform.version()
    machine = platform.machine()

    return (
        f"You are running {system}. "
        f"System version: {version}. "
        f"Architecture: {machine}."
    )


# --------------------------------------------------
# Battery Information
# --------------------------------------------------

def _battery_status() -> str:
    """Return the current battery status."""

    battery = psutil.sensors_battery()

    if battery is None:
        return "I cannot detect a battery on this computer."

    percentage = round(battery.percent)

    if battery.power_plugged:
        status = "and the charger is connected."
    else:
        status = "and the charger is not connected."

    return (
        f"Your battery is at {percentage} percent "
        f"{status}"
    )


# --------------------------------------------------
# Screen Analysis
# --------------------------------------------------

def _analyze_screen() -> str:
    """Capture and analyze the current screen."""

    try:
        screenshot = capture_screen()

        return analyze_image(
            screenshot,
            "Describe what is currently visible on this "
            "computer screen. Identify the main application "
            "or window and summarize the important visible "
            "information. Keep the answer concise.",
        )

    except Exception as error:
        print(f"Screen analysis error: {error}")

        return "I was unable to analyze the screen."


# --------------------------------------------------
# Main Command Processor
# --------------------------------------------------

def execute(command: str) -> str | None:
    """Execute a recognized JARVIS command."""

    normalized = command.casefold().strip()

    # --------------------------------------------------
    # Open Websites
    # --------------------------------------------------

    for name, url in WEBSITES.items():

        if normalized in {
            f"open {name}",
            f"launch {name}",
            f"go to {name}",
        }:

            webbrowser.open(url)

            return f"Opening {name.title()}."


    # --------------------------------------------------
    # Open Applications
    # --------------------------------------------------

    for name, application in APPLICATIONS.items():

        if normalized in {
            f"open {name}",
            f"launch {name}",
            f"start {name}",
        }:

            _open_application(application)

            return f"Opening {name.title()}."


    # --------------------------------------------------
    # Time
    # --------------------------------------------------

    if normalized in {
        "time",
        "what time is it",
        "tell me the time",
        "current time",
    }:

        current_time = dt.datetime.now().astimezone()

        return current_time.strftime(
            "It is %I:%M %p."
        )


    # --------------------------------------------------
    # Date
    # --------------------------------------------------

    if normalized in {
        "date",
        "what is the date",
        "what's the date",
        "today's date",
    }:

        today = dt.datetime.now().astimezone()

        return today.strftime(
            "Today is %A, %B %d, %Y."
        )


    # --------------------------------------------------
    # System Information
    # --------------------------------------------------

    if normalized in {
        "system information",
        "system info",
        "computer information",
        "computer info",
        "what computer am i using",
    }:

        return _system_info()


    # --------------------------------------------------
    # Battery
    # --------------------------------------------------

    if normalized in {
        "battery",
        "battery status",
        "battery level",
        "what is my battery level",
        "what's my battery level",
        "how much battery do i have",
        "how much battery is left",
    }:

        return _battery_status()


    # --------------------------------------------------
    # Screen Analysis
    # --------------------------------------------------

    if normalized in {
        "what is on my screen",
        "what's on my screen",
        "what is on the screen",
        "what's on the screen",
        "look at my screen",
        "describe my screen",
        "analyze my screen",
    }:

        return _analyze_screen()


    # --------------------------------------------------
    # Google Search
    # --------------------------------------------------

    result = _search(
        normalized,
        "search google for ",
        "https://www.google.com/search?q={query}",
        "Google",
    )

    if result:
        return result


    # --------------------------------------------------
    # YouTube Search
    # --------------------------------------------------

    result = _search(
        normalized,
        "search youtube for ",
        "https://www.youtube.com/results?search_query={query}",
        "YouTube",
    )

    if result:
        return result


    # --------------------------------------------------
    # No Command Matched
    # --------------------------------------------------

    return None