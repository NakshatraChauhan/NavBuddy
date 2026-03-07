from __future__ import annotations

import threading
from typing import Callable, Dict, Optional

import speech_recognition as sr


class VoiceController:
    def __init__(self, navigator, speech_engine, logger, permissions) -> None:
        self.navigator = navigator
        self.speech_engine = speech_engine
        self.logger = logger
        self.permissions = permissions
        self._recognizer = sr.Recognizer()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._command_map: Dict[str, Callable[[], str]] = {
            "start navigation": self.navigator.start_navigation,
            "stop navigation": self.navigator.stop_navigation,
            "describe scene": self.navigator.describe_scene_once,
            "stop scan": self.navigator.stop_scan,
            "status": self.navigator.status,
            "help": self.navigator.help,
        }

    def _resolve_command(self, spoken_text: str) -> Optional[str]:
        command = spoken_text.lower().strip()
        if command in self._command_map:
            return command
        for known in self._command_map:
            if known in command:
                return known
        return None

    def _listen_loop(self) -> None:
        self.logger.info("Voice listener started")

        if not self.permissions.microphone:
            self.logger.warning("Microphone permission denied; voice control disabled")
            self.speech_engine.speak("Microphone permission denied. Voice commands disabled.")
            return

        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.8)
                while self._running:
                    try:
                        audio = self._recognizer.listen(source, timeout=1, phrase_time_limit=4)
                    except sr.WaitTimeoutError:
                        continue

                    try:
                        spoken = self._recognizer.recognize_google(audio).lower().strip()
                        self.logger.info("Heard command: %s", spoken)
                        self.handle_command(spoken)
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError:
                        self.logger.warning("Speech recognition request failed; offline or API issue")
        except Exception:
            self.logger.exception("Microphone initialization failed")
            self.speech_engine.speak("Microphone not detected. Voice commands disabled.")

        self.logger.info("Voice listener stopped")

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def handle_command(self, raw_command: str) -> str:
        resolved = self._resolve_command(raw_command)
        if resolved:
            try:
                result = self._command_map[resolved]()
                self.logger.info("Executed command '%s' => %s", resolved, result)
                return result
            except Exception:
                self.logger.exception("Command execution failed: %s", resolved)
                message = "Sorry, command failed"
                self.speech_engine.speak(message)
                return message

        message = "Unknown command. Say help for available commands."
        self.speech_engine.speak(message)
        return message
