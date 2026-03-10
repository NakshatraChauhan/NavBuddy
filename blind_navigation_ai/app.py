from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Dict, List

from flask import Flask, jsonify, render_template, request

from depth_estimation import DepthEstimator
from navigation_engine import NavigationEngine
from object_detection import ObjectDetector
from scene_analyzer import combine_detections_with_depth, scene_summary

app = Flask(__name__)

detector = ObjectDetector(model_path="models/yolov8n.pt")
depth_estimator = DepthEstimator()
nav_engine = NavigationEngine()

latest_objects: List[Dict] = []
latest_nav: Dict = {"message": "Stopped", "speak": False, "action": "idle"}
metrics_lock = threading.Lock()
latencies_ms: Deque[float] = deque(maxlen=120)
fps_samples: Deque[float] = deque(maxlen=120)
last_frame_at = 0.0


def _record_metrics(latency_ms: float) -> None:
    global last_frame_at
    now = time.time()
    with metrics_lock:
        latencies_ms.append(latency_ms)
        if last_frame_at > 0:
            delta = now - last_frame_at
            if delta > 0:
                fps_samples.append(1.0 / delta)
        last_frame_at = now


def _metrics_snapshot() -> Dict:
    with metrics_lock:
        avg_latency = round(sum(latencies_ms) / len(latencies_ms), 2) if latencies_ms else 0.0
        avg_fps = round(sum(fps_samples) / len(fps_samples), 2) if fps_samples else 0.0
    detection_accuracy_proxy = 0.0 if detector.using_fallback else 0.75
    data = {
        "avg_latency_ms": avg_latency,
        "avg_fps": avg_fps,
        "detection_accuracy_proxy": detection_accuracy_proxy,
        "detector_mode": "fallback" if detector.using_fallback else "yolov8",
        "depth_mode": "fallback" if depth_estimator.using_fallback else "midas",
    }
    print(f"[METRICS] {data}")
    return data


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect_route():
    global latest_objects, latest_nav
    body = request.get_json(silent=True) or {}
    frame_b64 = body.get("frame")
    if not frame_b64:
        return jsonify({"error": "frame is required"}), 400

    t0 = time.perf_counter()
    frame = detector.decode_frame(frame_b64)
    raw = [d.__dict__ for d in detector.detect(frame)]
    depth_map = depth_estimator.estimate_depth_map(frame)
    objects = combine_detections_with_depth(raw, depth_estimator, depth_map, frame.shape)
    nav = nav_engine.decide(objects)
    latest_objects = objects
    latest_nav = nav

    latency_ms = (time.perf_counter() - t0) * 1000
    _record_metrics(latency_ms)
    metrics = _metrics_snapshot()

    return jsonify({"objects": objects, "navigation": nav, "metrics": metrics})


@app.route("/navigation", methods=["GET"])
def navigation_route():
    return jsonify({"navigation": latest_nav, "objects": latest_objects})


@app.route("/describe_scene", methods=["GET"])
def describe_scene_route():
    return jsonify({"summary": scene_summary(latest_objects), "objects": latest_objects})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
