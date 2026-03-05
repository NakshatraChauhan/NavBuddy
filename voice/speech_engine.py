"""Speech synthesis engine for guidance prompts."""
from __future__ import annotations

import threading

from utils.logger import configure_logger

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None


class SpeechEngine:
    """Speak text guidance with offline pyttsx3 when available."""

    def __init__(self) -> None:
        self.logger = configure_logger("SpeechEngine")
        self._engine = pyttsx3.init() if pyttsx3 else None

    def speak(self, message: str) -> None:
        self.logger.info("Voice: %s", message)
        if self._engine is None:
            return

        def worker() -> None:
            self._engine.say(message)
            self._engine.runAndWait()

        threading.Thread(target=worker, daemon=True).start()
