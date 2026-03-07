from __future__ import annotations

import threading
import time
from typing import Dict, Optional

import cv2


class Navigator:
    HELP_TEXT = (
        "Available commands are: "
        "start navigation, stop navigation, describe scene, stop scan, status, help."
    )

    def __init__(self, detector, scene_analyzer, speech_engine, logger, permissions, target_fps: float = 4.0) -> None:
        self.detector = detector
        self.scene_analyzer = scene_analyzer
        self.speech_engine = speech_engine
        self.logger = logger
        self.permissions = permissions
        self.target_fps = target_fps

        self._cap: Optional[cv2.VideoCapture] = None
        self._cap_lock = threading.Lock()

        self._scan_active = False
        self._scan_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self._last_alert = ""
        self._last_alert_ts = 0.0
        self._alert_cooldown_seconds = 2.5

    def _ensure_camera(self) -> bool:
        if not self.permissions.camera:
            self.logger.warning("Camera permission denied")
            return False

        with self._cap_lock:
            if self._cap and self._cap.isOpened():
                return True

            self._cap = cv2.VideoCapture(0)
            if not self._cap.isOpened():
                self.logger.error("Camera could not be opened")
                self._cap = None
                return False

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._cap.set(cv2.CAP_PROP_FPS, 15)
            self.logger.info("Camera opened successfully")
            return True

    def _release_camera_if_idle(self) -> None:
        with self._cap_lock:
            if self._scan_active:
                return
            if self._cap:
                self._cap.release()
                self._cap = None
                self.logger.info("Camera released")

    def _read_frame(self):
        with self._cap_lock:
            if not self._cap:
                return False, None
            return self._cap.read()

    def describe_scene_once(self) -> str:
        if not self.permissions.camera:
            message = "Camera permission denied"
            self.speech_engine.speak(message)
            return message

        if not self._ensure_camera():
            message = "Camera unavailable"
            self.speech_engine.speak(message)
            return message

        ok, frame = self._read_frame()
        if not ok or frame is None:
            message = "Could not capture camera frame"
            self.logger.error(message)
            self.speech_engine.speak(message)
            return message

        detections = self.detector.detect(frame)
        description = self.scene_analyzer.describe_scene(detections, frame.shape[1])
        self.speech_engine.speak(description)
        self._release_camera_if_idle()
        return description

    def _announce_with_cooldown(self, message: str) -> None:
        now = time.time()
        if message == self._last_alert and now - self._last_alert_ts < self._alert_cooldown_seconds:
            return

        self._last_alert = message
        self._last_alert_ts = now
        self.speech_engine.speak(message)

    def _scan_loop(self) -> None:
        self.logger.info("Navigation scanning loop started")
        interval = 1.0 / max(self.target_fps, 1.0)

        while not self._stop_event.is_set():
            started = time.monotonic()
            ok, frame = self._read_frame()
            if not ok or frame is None:
                self.logger.warning("Skipping frame during navigation scan")
                time.sleep(0.2)
                continue

            detections = self.detector.detect(frame)
            alert = self.scene_analyzer.navigation_alert(detections, frame.shape[1])
            self._announce_with_cooldown(alert)

            elapsed = time.monotonic() - started
            sleep_for = interval - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

        self.logger.info("Navigation scanning loop stopped")

    def start_navigation(self) -> str:
        if not self.permissions.camera:
            message = "Camera permission denied"
            self.speech_engine.speak(message)
            return message

        if self._scan_active:
            message = "Navigation is already active"
            self.speech_engine.speak(message)
            return message

        if not self._ensure_camera():
            message = "Cannot start navigation. Camera unavailable"
            self.speech_engine.speak(message)
            return message

        self._scan_active = True
        self._stop_event.clear()
        self._scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._scan_thread.start()

        message = "Navigation started"
        self.speech_engine.speak(message)
        return message

    def stop_navigation(self) -> str:
        if not self._scan_active:
            message = "Navigation is already stopped"
            self.speech_engine.speak(message)
            return message

        self._scan_active = False
        self._stop_event.set()
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=2)

        self._release_camera_if_idle()

        message = "Navigation stopped"
        self.speech_engine.speak(message)
        return message

    def stop_scan(self) -> str:
        return self.stop_navigation()

    def status(self) -> str:
        if self._scan_active:
            message = "Navigation active. Scanning environment."
        else:
            message = "Navigation inactive. Waiting for command."
        self.speech_engine.speak(message)
        return message

    def help(self) -> str:
        self.speech_engine.speak(self.HELP_TEXT)
        return self.HELP_TEXT

    def snapshot(self) -> Dict[str, object]:
        return {
            "navigation_active": self._scan_active,
            "commands": [
                "start navigation",
                "stop navigation",
                "describe scene",
                "stop scan",
                "status",
                "help",
            ],
            "permissions": {
                "camera": self.permissions.camera,
                "microphone": self.permissions.microphone,
                "gps": self.permissions.gps,
                "speaker": self.permissions.speaker,
            },
            "inference_ms": round(self.detector.last_inference_ms, 2),
        }
