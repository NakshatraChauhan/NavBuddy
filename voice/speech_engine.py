from __future__ import annotations

import threading

import pyttsx3


class SpeechEngine:
    def __init__(self, logger) -> None:
        self.logger = logger
        self._lock = threading.Lock()
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

    def speak(self, text: str) -> None:
        if not text:
            return

        with self._lock:
            try:
                self.logger.info("TTS: %s", text)
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                self.logger.exception("TTS failed for text: %s", text)
