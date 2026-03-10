from flask import Flask, jsonify, render_template, request

from gps_module import describe_location
from navigation_logic import NavigationAdvisor
from object_detection import AsyncDetector
from scene_description import build_scene_summary

app = Flask(__name__)
detector = AsyncDetector()
advisor = NavigationAdvisor()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect_objects", methods=["POST"])
def detect_objects():
    body = request.get_json(silent=True) or {}
    frame_b64 = body.get("frame")
    if not frame_b64:
        return jsonify({"error": "Missing frame"}), 400

    detections = detector.process_frame(frame_b64)
    guidance = advisor.guidance(detections)
    return jsonify({"detections": detections, "guidance": guidance})


@app.route("/describe_scene", methods=["GET"])
def describe_scene():
    detections = detector.latest()
    summary = build_scene_summary(detections)
    return jsonify({"summary": summary, "detections": detections})


@app.route("/gps_location", methods=["POST"])
def gps_location():
    body = request.get_json(silent=True) or {}
    lat = body.get("latitude")
    lon = body.get("longitude")
    if lat is None or lon is None:
        return jsonify({"error": "latitude and longitude are required"}), 400
    result = describe_location(float(lat), float(lon))
    return jsonify(result)


@app.route("/process_voice", methods=["POST"])
def process_voice():
    body = request.get_json(silent=True) or {}
    command = (body.get("command") or "").strip().lower()

    mapped = {
        "start navigation": "Navigation started. I will monitor obstacles continuously.",
        "stop navigation": "Navigation paused.",
        "guide me forward": "Scanning now. I will suggest the safest direction.",
        "describe surroundings": build_scene_summary(detector.latest()),
        "what is in front of me": build_scene_summary(detector.latest()),
        "where am i": "Fetching your location now.",
    }
    response = mapped.get(command, "Command received. Please say start navigation or describe surroundings.")
    return jsonify({"response": response, "command": command})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
