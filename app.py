from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from ai.detector import ObstacleDetector
from ai.scene_analyzer import SceneAnalyzer
from navigation.navigator import Navigator
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
        self.ready = False
        self.init_error = ""

    def initialize(self) -> None:
        try:
            self.detector = ObstacleDetector("models/yolov8n.pt", logger=self.logger)
            self.scene_analyzer = SceneAnalyzer(logger=self.logger)
            self.speech_engine = SpeechEngine(logger=self.logger)
            self.navigator = Navigator(
                detector=self.detector,
                scene_analyzer=self.scene_analyzer,
                speech_engine=self.speech_engine,
                logger=self.logger,
            )
            self.voice_controller = VoiceController(
                navigator=self.navigator,
                speech_engine=self.speech_engine,
                logger=self.logger,
            )
            self.voice_controller.start()
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
    app.run(host="0.0.0.0", port=5000, debug=False)
