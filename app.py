from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

from ai.detector import ObstacleDetector
from ai.scene_analyzer import SceneAnalyzer
from navigation.navigator import Navigator
from permissions.permission_manager import PermissionManager
from utils.logger import configure_logger
from voice.speech_engine import SpeechEngine
from voice.voice_controller import VoiceController

app = Flask(__name__)
logger = configure_logger()


class SystemContainer:
    def __init__(self):
        self.logger = logger
        self.detector = None
        self.scene_analyzer = None
        self.speech_engine = None
        self.navigator = None
        self.voice_controller = None
        self.permission_manager = None
        self.ready = False
        self.init_error = ""

    def initialize(self) -> None:
        self.permission_manager = PermissionManager(logger=self.logger)

        try:
            model_path = os.getenv("BLINDNAV_MODEL_PATH", "models/yolov8n.pt")
            target_fps = float(os.getenv("BLINDNAV_TARGET_FPS", "4"))

            # 1) Load YOLO model
            self.detector = ObstacleDetector(model_path, logger=self.logger)
            self.scene_analyzer = SceneAnalyzer(logger=self.logger)

            # 2) Initialize speech engine
            self.speech_engine = SpeechEngine(logger=self.logger)

            # 3) Ask for hardware permissions
            permissions = self.permission_manager.request_all()
            self.speech_engine.set_enabled(permissions.speaker)
            if not permissions.speaker:
                self.logger.warning("Speaker permission denied; audio feedback muted")

            if not permissions.camera:
                self.speech_engine.speak("Camera permission denied")
            if not permissions.microphone:
                self.speech_engine.speak("Microphone permission denied")
            if not permissions.gps:
                self.logger.info("GPS permission denied. Outdoor context disabled.")

            self.navigator = Navigator(
                detector=self.detector,
                scene_analyzer=self.scene_analyzer,
                speech_engine=self.speech_engine,
                logger=self.logger,
                permissions=permissions,
                target_fps=target_fps,
            )

            self.voice_controller = VoiceController(
                navigator=self.navigator,
                speech_engine=self.speech_engine,
                logger=self.logger,
                permissions=permissions,
            )

            # 4) Start voice command listener
            self.voice_controller.start()

            # 5) Wait for commands
            self.ready = True
            self.logger.info("System initialized")
            self.speech_engine.speak("Blind Navigation Assistant is ready.")
        except Exception as exc:
            self.ready = False
            self.init_error = str(exc)
            self.logger.exception("System initialization failed")


system = SystemContainer()
system.initialize()


@app.route("/")
def index():
    state = system.navigator.snapshot() if system.ready else {}
    return render_template(
        "index.html",
        ready=system.ready,
        error=system.init_error,
        commands=state.get("commands", []),
        navigation_active=state.get("navigation_active", False),
        permissions=state.get("permissions", {}),
        inference_ms=state.get("inference_ms", 0),
    )


@app.route("/api/status", methods=["GET"])
def api_status():
    if not system.ready:
        return jsonify({"ready": False, "error": system.init_error}), 500
    return jsonify({"ready": True, **system.navigator.snapshot()})


@app.route("/api/command", methods=["POST"])
def api_command():
    if not system.ready:
        return jsonify({"ok": False, "message": "System not ready", "error": system.init_error}), 500

    payload = request.get_json(silent=True) or {}
    command = str(payload.get("command", "")).strip().lower()
    if not command:
        return jsonify({"ok": False, "message": "Command is required"}), 400

    message = system.voice_controller.handle_command(command)
    return jsonify({"ok": True, "message": message, **system.navigator.snapshot()})


if __name__ == "__main__":
    app.run(host=os.getenv("BLINDNAV_HOST", "0.0.0.0"), port=int(os.getenv("BLINDNAV_PORT", "5000")), debug=False)
