"""Basic integration checks for BlindNav AI APIs."""
from __future__ import annotations

import base64

import cv2
import numpy as np

from app import app


client = app.test_client()


def make_test_image_data() -> str:
    frame = np.zeros((320, 320, 3), dtype=np.uint8)
    cv2.rectangle(frame, (90, 60), (220, 260), (255, 255, 255), -1)
    ok, buff = cv2.imencode(".jpg", frame)
    assert ok
    return "data:image/jpeg;base64," + base64.b64encode(buff.tobytes()).decode("utf-8")


def run() -> None:
    home = client.get("/")
    assert home.status_code == 200

    detect = client.post("/detect", json={"image": make_test_image_data()})
    assert detect.status_code == 200
    detections = detect.get_json().get("detections", [])

    risk = client.post("/risk", json={"detections": detections})
    assert risk.status_code == 200

    route = client.get("/route")
    assert route.status_code == 200
    assert "instructions" in route.get_json()

    emergency = client.post("/emergency", json={"lat": 37.7749, "lon": -122.4194, "phone": "+10000000000"})
    assert emergency.status_code == 200
    assert emergency.get_json()["status"] == "activated"

    print("BlindNav AI checks passed.")


if __name__ == "__main__":
    run()
