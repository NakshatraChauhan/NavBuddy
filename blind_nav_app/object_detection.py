import base64
import io
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import cv2
import numpy as np
from PIL import Image

TARGET_CLASSES = {
    "person",
    "car",
    "motorcycle",
    "bicycle",
    "chair",
    "table",
    "bench",
    "traffic light",
}

APPROX_WIDTH_METERS = {
    "person": 0.45,
    "car": 1.8,
    "motorcycle": 0.8,
    "bicycle": 0.6,
    "chair": 0.5,
    "table": 1.2,
    "bench": 1.2,
    "traffic light": 0.4,
    "unknown obstacle": 0.6,
}


@dataclass
class DetectionResult:
    label: str
    confidence: float
    bbox: List[int]
    distance_m: float
    distance_label: str
    direction: str


class YOLODetector:
    def __init__(self):
        self.model = None
        self.model_type = None
        self.focal_length_px = 650.0
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO

            self.model = YOLO("yolov8n.pt")
            self.model_type = "ultralytics"
        except Exception:
            self.model = None
            self.model_type = None

    @staticmethod
    def decode_frame(base64_frame: str) -> np.ndarray:
        frame_bytes = base64.b64decode(base64_frame.split(",")[-1])
        image = Image.open(io.BytesIO(frame_bytes)).convert("RGB")
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return frame

    def _distance_from_bbox(self, label: str, bbox: List[int]) -> float:
        x1, y1, x2, y2 = bbox
        width_px = max(1, x2 - x1)
        real_width = APPROX_WIDTH_METERS.get(label, APPROX_WIDTH_METERS["unknown obstacle"])
        distance = (real_width * self.focal_length_px) / width_px
        return round(float(max(0.2, min(distance, 15.0))), 2)

    @staticmethod
    def _distance_label(distance_m: float) -> str:
        if distance_m < 1.0:
            return "Very Close"
        if distance_m <= 2.0:
            return "Close"
        return "Safe"

    @staticmethod
    def _direction(frame_width: int, bbox: List[int]) -> str:
        x1, _, x2, _ = bbox
        center = (x1 + x2) / 2
        left_third = frame_width / 3
        right_third = 2 * frame_width / 3
        if center < left_third:
            return "Left"
        if center > right_third:
            return "Right"
        return "Center"

    def _heuristic_fallback(self, frame: np.ndarray) -> List[DetectionResult]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 80, 160)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections: List[DetectionResult] = []
        h, w = frame.shape[:2]
        min_area = (w * h) * 0.02
        for c in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
            area = cv2.contourArea(c)
            if area < min_area:
                continue
            x, y, cw, ch = cv2.boundingRect(c)
            bbox = [int(x), int(y), int(x + cw), int(y + ch)]
            dist = self._distance_from_bbox("unknown obstacle", bbox)
            detections.append(
                DetectionResult(
                    label="unknown obstacle",
                    confidence=0.45,
                    bbox=bbox,
                    distance_m=dist,
                    distance_label=self._distance_label(dist),
                    direction=self._direction(w, bbox),
                )
            )
        return detections

    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        h, w = frame.shape[:2]
        if self.model is None:
            return self._heuristic_fallback(frame)

        detections: List[DetectionResult] = []
        result = self.model.predict(frame, verbose=False, imgsz=640, conf=0.35)[0]
        for box in result.boxes:
            cls_id = int(box.cls.item())
            label = self.model.names[cls_id]
            if label not in TARGET_CLASSES:
                continue
            conf = float(box.conf.item())
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            bbox = [x1, y1, x2, y2]
            distance = self._distance_from_bbox(label, bbox)
            detections.append(
                DetectionResult(
                    label=label,
                    confidence=round(conf, 2),
                    bbox=bbox,
                    distance_m=distance,
                    distance_label=self._distance_label(distance),
                    direction=self._direction(w, bbox),
                )
            )
        return detections


class AsyncDetector:
    def __init__(self):
        self.detector = YOLODetector()
        self._latest_result: List[Dict] = []
        self._lock = threading.Lock()
        self._last_process_at = 0.0
        self._min_interval = 0.25

    def process_frame(self, frame_b64: str) -> List[Dict]:
        now = time.time()
        if now - self._last_process_at < self._min_interval:
            with self._lock:
                return self._latest_result

        frame = self.detector.decode_frame(frame_b64)
        detections = self.detector.detect(frame)
        payload = [d.__dict__ for d in detections]

        with self._lock:
            self._latest_result = payload
            self._last_process_at = now
        return payload

    def latest(self) -> List[Dict]:
        with self._lock:
            return self._latest_result
