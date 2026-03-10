from __future__ import annotations


class VoiceFeedback:
    """Server-side TTS helper (optional; browser SpeechSynthesis remains primary)."""

    def __init__(self):
        self.engine = None
        self.enabled = False
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 170)
            self.enabled = True
        except Exception:
            self.enabled = False

    def speak(self, text: str) -> None:
        if not self.enabled or not text:
            return
        self.engine.say(text)
        self.engine.runAndWait()
