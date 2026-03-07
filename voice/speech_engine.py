from __future__ import annotations

import threading

import pyttsx3


class SpeechEngine:
    def __init__(self, logger) -> None:
        self.logger = logger
        self._lock = threading.Lock()
        self._enabled = True
        self.engine = self._init_engine()

    def _init_engine(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)
            return engine
        except Exception:
            self.logger.exception("Failed to initialize text-to-speech engine")
            raise

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.logger.info("Speech output enabled=%s", enabled)

    def speak(self, text: str) -> None:
        if not text:
            return

        self.logger.info("TTS queued: %s", text)
        if not self._enabled:
            return

        with self._lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                self.logger.exception("TTS failed for text: %s", text)
