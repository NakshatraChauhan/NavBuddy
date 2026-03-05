"""YOLOv8 object detector wrapper."""
from __future__ import annotations

from typing import Any, Dict, List

import cv2
import numpy as np

from ai.distance_estimator import DistanceEstimator
from utils.helpers import normalize_direction
from utils.logger import configure_logger

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover - dependency may be absent
    YOLO = None


TARGET_LABELS = {
    "person",
    "car",
    "bicycle",
    "motorcycle",
    "chair",
    "dining table",
    "traffic light",
}


class YOLODetector:
    """CPU-friendly detection wrapper for static images and camera frames."""

    def __init__(self, model_path: str, focal_length_px: float = 650.0) -> None:
        self.logger = configure_logger("YOLODetector")
        self.distance_estimator = DistanceEstimator(focal_length_px)
        self.model = None
        if YOLO and model_path:
            try:
                self.model = YOLO(model_path)
            except Exception as exc:
                self.logger.warning("Model load failed (%s); using fallback contour detector.", exc)
        if self.model is None:
            self.logger.warning("Ultralytics model unavailable; using fallback contour detector.")

    def _fallback_detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        for contour in contours[:5]:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h < 2500:
                continue
            est = self.distance_estimator.estimate("wall", h)
            detections.append(
                {
                    "label": "wall",
                    "confidence": 0.4,
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "center": [float(x + w / 2), float(y + h / 2)],
                    "direction": normalize_direction(x + w / 2, frame.shape[1]),
                    "distance_m": est.distance_m,
                    "distance_class": est.distance_class,
                    "moving": False,
                }
            )
        return detections

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Run object detection and annotate distance/direction attributes."""
        if frame is None or frame.size == 0:
            return []
        if self.model is None:
            return self._fallback_detect(frame)

        results = self.model.predict(frame, imgsz=640, conf=0.35, verbose=False, device="cpu")
        detections: List[Dict[str, Any]] = []

        for result in results:
            names = result.names
            for box in result.boxes:
                cls = int(box.cls[0])
                label = names.get(cls, str(cls))
                if label == "dining table":
                    mapped_label = "table"
                else:
                    mapped_label = label

                if label not in TARGET_LABELS and mapped_label not in {"table"}:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                w = max(x2 - x1, 1.0)
                h = max(y2 - y1, 1.0)
                cx, cy = x1 + w / 2, y1 + h / 2
                est = self.distance_estimator.estimate(mapped_label, h)
                detections.append(
                    {
                        "label": mapped_label,
                        "confidence": float(box.conf[0]),
                        "bbox": [int(x1), int(y1), int(w), int(h)],
                        "center": [float(cx), float(cy)],
                        "direction": normalize_direction(cx, frame.shape[1]),
                        "distance_m": est.distance_m,
                        "distance_class": est.distance_class,
                        "moving": False,
                    }
                )
        return detections
