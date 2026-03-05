"""BlindNav AI Flask application."""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request

from ai.object_tracker import ObjectTracker
from ai.yolo_detector import YOLODetector
from config import CONFIG
from emergency.emergency_handler import EmergencyHandler
from navigation.graph_builder import GraphBuilder
from navigation.gps_manager import GPSManager
from navigation.osm_parser import OSMParser
from navigation.route_engine import RouteEngine
from risk.alert_manager import AlertManager
from risk.risk_classifier import RiskClassifier
from voice.speech_engine import SpeechEngine
from utils.logger import configure_logger

app = Flask(__name__)
app.config["SECRET_KEY"] = CONFIG.SECRET_KEY
logger = configure_logger("BlindNavApp", str(CONFIG.LOG_PATH))


def decode_image_from_data_url(data_url: str) -> np.ndarray:
    """Convert base64 image data URL to OpenCV BGR frame."""
    if "," in data_url:
        encoded = data_url.split(",", 1)[1]
    else:
        encoded = data_url
    image_bytes = base64.b64decode(encoded)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return frame


detector = YOLODetector(str(CONFIG.MODEL_PATH), CONFIG.FOCAL_LENGTH_PX)
tracker = ObjectTracker()
risk_classifier = RiskClassifier()
alert_manager = AlertManager()
speech_engine = SpeechEngine()
gps_manager = GPSManager()
emergency_handler = EmergencyHandler(CONFIG.SMS_APPROVED)
executor = ThreadPoolExecutor(max_workers=2)

map_data = OSMParser(CONFIG.OSM_DATA_PATH).load()
graph, node_map = GraphBuilder().build(map_data)
route_engine = RouteEngine(graph, node_map)


@app.get("/")
def index() -> str:
    return render_template("index.html", approvals=CONFIG)


@app.get("/navigation")
def navigation() -> str:
    return render_template("navigation.html", approvals=CONFIG)


@app.post("/detect")
def detect() -> Any:
    if not CONFIG.CAMERA_APPROVED:
        return jsonify({"error": "Camera permission not approved."}), 403

    payload = request.get_json(silent=True) or {}
    image_data = payload.get("image")
    if not image_data:
        return jsonify({"error": "No image payload supplied."}), 400

    frame = decode_image_from_data_url(image_data)
    future = executor.submit(detector.detect, frame)
    detections = tracker.update(future.result())
    return jsonify({"detections": detections})


@app.post("/risk")
def risk() -> Any:
    payload = request.get_json(silent=True) or {}
    detections: List[Dict[str, Any]] = payload.get("detections", [])
    risk_results = []

    for det in detections:
        risk_level = risk_classifier.classify(det)
        det["risk_level"] = risk_level

        if risk_level == "HIGH":
            msg = f"{det['label']} approaching from {det['direction']}"
            alert_key = f"{det.get('track_id', 'x')}-{msg}"
            if alert_manager.should_alert(alert_key):
                speech_engine.speak(msg)
                det["voice_alert"] = msg
                if det.get("moving"):
                    det["vibration_pattern"] = [120, 80, 120]
                else:
                    det["vibration_pattern"] = [500]
        risk_results.append(det)

    return jsonify({"results": risk_results})


@app.get("/route")
def route() -> Any:
    if not CONFIG.GPS_APPROVED:
        return jsonify({"error": "GPS permission not approved."}), 403

    start_lat = float(request.args.get("start_lat", "37.7749"))
    start_lon = float(request.args.get("start_lon", "-122.4194"))
    end_lat = float(request.args.get("end_lat", "37.7755"))
    end_lon = float(request.args.get("end_lon", "-122.4180"))

    route_data = route_engine.build_route(start_lat, start_lon, end_lat, end_lon)
    return jsonify(route_data)


@app.post("/emergency")
def emergency() -> Any:
    payload = request.get_json(silent=True) or {}
    lat = float(payload.get("lat", gps_manager.get_current().lat))
    lon = float(payload.get("lon", gps_manager.get_current().lon))
    phone = payload.get("phone") if CONFIG.SMS_APPROVED else None

    gps_manager.update(lat, lon)
    response = emergency_handler.trigger(lat=lat, lon=lon, phone_number=phone)
    speech_engine.speak(response["message"])
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
