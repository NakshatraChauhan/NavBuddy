from __future__ import annotations

import threading
from typing import Callable, Dict

import speech_recognition as sr


class VoiceController:
    def __init__(self, navigator, speech_engine, logger) -> None:
        self.navigator = navigator
        self.speech_engine = speech_engine
        self.logger = logger
        self._recognizer = sr.Recognizer()
        self._running = False
        self._thread = None

        self._command_map: Dict[str, Callable[[], str]] = {
            "start navigation": self.navigator.start_navigation,
            "stop navigation": self.navigator.stop_navigation,
            "describe scene": self.navigator.describe_scene_once,
            "stop scan": self.navigator.stop_scan,
            "status": self.navigator.status,
            "help": self.navigator.help,
        }

    def _listen_loop(self) -> None:
        self.logger.info("Voice listener started")

        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.8)
                while self._running:
                    try:
                        audio = self._recognizer.listen(source, timeout=1, phrase_time_limit=4)
                    except sr.WaitTimeoutError:
                        continue

                    try:
                        command = self._recognizer.recognize_google(audio).lower().strip()
                        self.logger.info("Heard command: %s", command)
                        self.handle_command(command)
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError:
                        self.logger.warning("Speech recognition request failed; offline or API issue")
        except Exception:
            self.logger.exception("Microphone initialization failed")
            self.speech_engine.speak("Microphone unavailable. Voice control is disabled.")

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
        command = raw_command.lower().strip()
        if command in self._command_map:
            try:
                result = self._command_map[command]()
                self.logger.info("Executed command '%s' => %s", command, result)
                return result
            except Exception:
                self.logger.exception("Command execution failed: %s", command)
                message = "Sorry, command failed."
                self.speech_engine.speak(message)
                return message

        message = "Unknown command. Say help for available commands."
        self.speech_engine.speak(message)
        return message
