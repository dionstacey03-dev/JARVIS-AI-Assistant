"""Desktop command center for JARVIS."""

from __future__ import annotations

import datetime as dt
import threading
import tkinter as tk
from tkinter import scrolledtext

from jarvis import process_command
from listen import listen
from voice import speak


class JarvisApp(tk.Tk):
    """A responsive, keyboard-friendly interface for JARVIS."""

    BG = "#080d18"
    SURFACE = "#0f1728"
    SURFACE_ALT = "#17233b"
    BORDER = "#243451"
    TEXT = "#eff5ff"
    MUTED = "#91a2c1"
    CYAN = "#57ddff"
    GREEN = "#70e6b4"
    AMBER = "#ffc96b"
    ERROR = "#ff9baa"

    def __init__(self) -> None:
        super().__init__()
        self.title("JARVIS — Command Center")
        self.geometry("1120x720")
        self.minsize(880, 590)
        self.configure(bg=self.BG)
        self.option_add("*tearOff", False)

        self.voice_enabled = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="ONLINE")
        self.status_detail = tk.StringVar(value="Ready for your next request")
        self.clock = tk.StringVar()
        self._busy = False
        self._closing = False
        self._build_ui()
        self._add_message("JARVIS", "Systems initialized. What can I help you with?", "assistant")
        self._update_clock()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg=self.BG, padx=32, pady=23)
        header.pack(fill="x")
        tk.Label(header, text="JARVIS", font=("Segoe UI", 26, "bold"), bg=self.BG, fg=self.CYAN).pack(side="left")
        tk.Label(header, text="COMMAND CENTER", font=("Segoe UI", 10, "bold"), bg=self.BG, fg=self.MUTED).pack(side="left", padx=(14, 0), pady=(10, 0))
        tk.Label(header, textvariable=self.clock, font=("Cascadia Mono", 11), bg=self.BG, fg=self.TEXT).pack(side="right", pady=(8, 0))

        main = tk.Frame(self, bg=self.BG, padx=32)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=4, minsize=500)
        main.columnconfigure(1, weight=1, minsize=220)
        main.rowconfigure(0, weight=1)

        console = self._panel(main)
        console.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        title_row = tk.Frame(console, bg=self.SURFACE)
        title_row.pack(fill="x", padx=20, pady=(18, 0))
        tk.Label(title_row, text="ACTIVITY", font=("Segoe UI", 10, "bold"), bg=self.SURFACE, fg=self.MUTED).pack(side="left")
        self.clear_button = self._text_button(title_row, "Clear", self._clear_activity)
        self.clear_button.pack(side="right")
        self.transcript = scrolledtext.ScrolledText(
            console, wrap="word", state="disabled", relief="flat", bd=0,
            font=("Segoe UI", 11), bg=self.SURFACE, fg=self.TEXT,
            insertbackground=self.TEXT, padx=20, pady=15, spacing3=5,
            selectbackground="#294b70", highlightthickness=0,
        )
        self.transcript.pack(fill="both", expand=True, pady=(0, 5))
        self.transcript.tag_configure("user", foreground=self.CYAN, font=("Segoe UI", 10, "bold"))
        self.transcript.tag_configure("assistant", foreground=self.GREEN, font=("Segoe UI", 10, "bold"))
        self.transcript.tag_configure("meta", foreground=self.MUTED, font=("Cascadia Mono", 9))
        self.transcript.tag_configure("body", foreground=self.TEXT, font=("Segoe UI", 11))

        sidebar = self._panel(main)
        sidebar.grid(row=0, column=1, sticky="nsew")
        self._build_sidebar(sidebar)

        composer = tk.Frame(self, bg=self.BG, padx=32, pady=22)
        composer.pack(fill="x")
        entry_shell = tk.Frame(composer, bg=self.SURFACE_ALT, highlightbackground=self.BORDER, highlightthickness=1)
        entry_shell.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input = tk.Entry(entry_shell, font=("Segoe UI", 12), bg=self.SURFACE_ALT, fg=self.TEXT,
                              insertbackground=self.TEXT, relief="flat", bd=0)
        self.input.pack(fill="x", padx=16, pady=13)
        self.input.bind("<Return>", lambda _: self.submit())
        self.input.bind("<Escape>", lambda _: self.input.delete(0, "end"))
        self.input.focus_set()
        self.send_button = self._button(composer, "Send", self.submit)
        self.send_button.pack(side="left", padx=(0, 8))
        self.mic_button = self._button(composer, "Listen", self.start_listening, accent=True)
        self.mic_button.pack(side="left")

    def _build_sidebar(self, sidebar: tk.Frame) -> None:
        status_area = tk.Frame(sidebar, bg=self.SURFACE)
        status_area.pack(fill="x", padx=20, pady=(19, 0))
        tk.Label(status_area, text="SYSTEM STATUS", font=("Segoe UI", 10, "bold"), bg=self.SURFACE, fg=self.MUTED).pack(anchor="w")
        status_row = tk.Frame(status_area, bg=self.SURFACE)
        status_row.pack(anchor="w", pady=(10, 2))
        self.status_dot = tk.Label(status_row, text="●", font=("Segoe UI", 13), bg=self.SURFACE, fg=self.GREEN)
        self.status_dot.pack(side="left")
        tk.Label(status_row, textvariable=self.status, font=("Segoe UI", 11, "bold"), bg=self.SURFACE, fg=self.TEXT).pack(side="left", padx=(5, 0))
        tk.Label(status_area, textvariable=self.status_detail, font=("Segoe UI", 9), bg=self.SURFACE, fg=self.MUTED, wraplength=190, justify="left").pack(anchor="w", pady=(0, 16))
        self._divider(sidebar).pack(fill="x", padx=20, pady=12)
        tk.Label(sidebar, text="QUICK ACTIONS", font=("Segoe UI", 10, "bold"), bg=self.SURFACE, fg=self.MUTED).pack(anchor="w", padx=20)
        actions = (("Open YouTube", "open youtube"), ("Open Calculator", "open calculator"),
                   ("Current time", "what time is it"), ("Remembered name", "what is my name"))
        for label, command in actions:
            self._button(sidebar, label, lambda value=command: self.submit(value), small=True).pack(fill="x", padx=20, pady=(9, 0))
        self._divider(sidebar).pack(fill="x", padx=20, pady=(18, 13))
        tk.Checkbutton(sidebar, text="Voice responses", variable=self.voice_enabled, selectcolor=self.SURFACE_ALT,
                       activebackground=self.SURFACE, activeforeground=self.TEXT, bg=self.SURFACE, fg=self.TEXT,
                       font=("Segoe UI", 10), bd=0, highlightthickness=0, cursor="hand2").pack(anchor="w", padx=16)
        tk.Label(sidebar, text="Enter to send  •  Esc to clear", font=("Segoe UI", 8), bg=self.SURFACE, fg=self.MUTED).pack(anchor="w", padx=20, pady=(8, 0))

    def _panel(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bg=self.SURFACE, highlightbackground=self.BORDER, highlightthickness=1)

    def _divider(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bg=self.BORDER, height=1)

    def _text_button(self, parent: tk.Widget, text: str, command: object) -> tk.Button:
        return tk.Button(parent, text=text, command=command, cursor="hand2", relief="flat", bd=0,
                         font=("Segoe UI", 9, "bold"), bg=self.SURFACE, fg=self.CYAN,
                         activebackground=self.SURFACE, activeforeground=self.TEXT)

    def _button(self, parent: tk.Widget, text: str, command: object, small: bool = False, accent: bool = False) -> tk.Button:
        return tk.Button(parent, text=text, command=command, cursor="hand2", relief="flat", bd=0,
                         font=("Segoe UI", 10 if small else 11, "bold"), padx=14 if small else 19,
                         pady=8 if small else 11, bg=self.CYAN if accent else self.SURFACE_ALT,
                         fg=self.BG if accent else self.TEXT, activebackground="#a4efff" if accent else "#263a60",
                         activeforeground=self.BG if accent else self.TEXT, disabledforeground=self.MUTED)

    def _add_message(self, speaker: str, message: str, tag: str) -> None:
        timestamp = dt.datetime.now().strftime("%H:%M")
        self.transcript.configure(state="normal")
        self.transcript.insert("end", f"{timestamp}  ", "meta")
        self.transcript.insert("end", f"{speaker}\n", tag)
        self.transcript.insert("end", f"{message.strip()}\n\n", "body")
        self.transcript.configure(state="disabled")
        self.transcript.see("end")

    def _clear_activity(self) -> None:
        if self._busy:
            return
        self.transcript.configure(state="normal")
        self.transcript.delete("1.0", "end")
        self.transcript.configure(state="disabled")
        self._add_message("JARVIS", "Activity log cleared. I am ready when you are.", "assistant")

    def submit(self, command: str | None = None) -> None:
        if self._busy or self._closing:
            return
        text = command or self.input.get().strip()
        if not text:
            self.input.focus_set()
            return
        self.input.delete(0, "end")
        self._add_message("YOU", text, "user")
        self._set_state("PROCESSING", "Working on your request")
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text: str) -> None:
        try:
            response, should_exit = process_command(text)
        except Exception:
            response, should_exit = "I ran into a problem while completing that request. Please try again.", False
        if not self._closing:
            self.after(0, self._complete_response, response, should_exit)

    def _complete_response(self, response: str, should_exit: bool) -> None:
        if self._closing:
            return
        self._add_message("JARVIS", response, "assistant")
        self._set_state("ONLINE", "Ready for your next request")
        if self.voice_enabled.get() and response:
            threading.Thread(target=speak, args=(response,), daemon=True).start()
        if should_exit:
            self._set_state("SHUTTING DOWN", "Closing command center")
            self.after(900, self._close)

    def start_listening(self) -> None:
        if self._busy or self._closing:
            return
        self._set_state("LISTENING", "Speak when you are ready")
        threading.Thread(target=self._listen_once, daemon=True).start()

    def _listen_once(self) -> None:
        try:
            heard = listen()
        except Exception:
            heard = None
        if not self._closing:
            self.after(0, self._received_speech, heard)

    def _received_speech(self, heard: str | None) -> None:
        if self._closing:
            return
        if heard:
            self._set_state("ONLINE", "Voice command received")
            self.submit(heard)
        else:
            self._set_state("ONLINE", "Ready for your next request")
            self._add_message("JARVIS", "I did not catch that. Please try again.", "assistant")

    def _set_state(self, state: str, detail: str) -> None:
        self._busy = state in {"PROCESSING", "LISTENING"}
        self.status.set(state)
        self.status_detail.set(detail)
        color = self.GREEN if state == "ONLINE" else self.AMBER if self._busy else self.ERROR
        self.status_dot.configure(fg=color)
        enabled = "disabled" if self._busy else "normal"
        self.mic_button.configure(state=enabled)
        self.send_button.configure(state=enabled)
        self.clear_button.configure(state=enabled)

    def _update_clock(self) -> None:
        if self._closing:
            return
        self.clock.set(dt.datetime.now().strftime("%A  |  %I:%M:%S %p"))
        self.after(1000, self._update_clock)

    def _close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.destroy()


def launch() -> None:
    """Start the desktop command center."""
    JarvisApp().mainloop()
