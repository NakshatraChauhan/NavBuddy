from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class PermissionState:
    camera: bool = False
    microphone: bool = False
    gps: bool = False
    speaker: bool = False


class PermissionManager:
    """Manages explicit hardware permissions for safety-critical features."""

    QUESTIONS = {
        "camera": "Camera access is required to detect obstacles. Do you allow camera access? (yes/no): ",
        "microphone": "Microphone access is required for voice commands. Do you allow microphone access? (yes/no): ",
        "gps": "GPS access can improve outdoor navigation context. Do you allow GPS access? (yes/no): ",
        "speaker": "Audio speaker access is required for spoken feedback. Do you allow speaker access? (yes/no): ",
    }

    def __init__(self, logger) -> None:
        self.logger = logger
        self.state = PermissionState()

    @staticmethod
    def _to_bool(value: str) -> bool:
        return value.strip().lower() in {"y", "yes", "true", "1", "allow"}

    def _ask(self, hardware: str) -> bool:
        env_key = f"BLINDNAV_PERMISSION_{hardware.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            allowed = self._to_bool(env_value)
            self.logger.info("Permission %s from env=%s -> %s", hardware, env_value, allowed)
            return allowed

        auto_approve = self._to_bool(os.getenv("BLINDNAV_AUTO_APPROVE", "false"))
        if auto_approve:
            self.logger.info("Auto-approving %s permission", hardware)
            return True

        try:
            response = input(self.QUESTIONS[hardware])
            allowed = self._to_bool(response)
            self.logger.info("Permission prompt %s -> %s", hardware, allowed)
            return allowed
        except EOFError:
            self.logger.warning("Non-interactive input: %s permission denied by default", hardware)
            return False

    def request_all(self) -> PermissionState:
        self.state.camera = self._ask("camera")
        self.state.microphone = self._ask("microphone")
        self.state.gps = self._ask("gps")
        self.state.speaker = self._ask("speaker")
        return self.state

    def as_dict(self) -> Dict[str, bool]:
        return {
            "camera": self.state.camera,
            "microphone": self.state.microphone,
            "gps": self.state.gps,
            "speaker": self.state.speaker,
        }
