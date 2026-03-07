from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import cv2
import numpy as np
from ultralytics import YOLO


@dataclass
class Detection:
    label: str
    confidence: float
    box: List[float]


class ObstacleDetector:
    """YOLOv8-based obstacle detector for CPU-first real-time processing."""

    INTEREST_CLASSES = {
        "person",
        "car",
        "bicycle",
        "motorcycle",
        "chair",
        "dining table",
        "stairs",
        "door",
        "wall",
    }

    NORMALIZED_NAMES: Dict[str, str] = {
        "dining table": "table",
    }

    def __init__(self, model_path: str, logger) -> None:
        self.logger = logger
        self.model_path = model_path
        self.model = self._load_model()

    def _load_model(self):
        try:
            model = YOLO(self.model_path)
            self.logger.info("YOLO model loaded from %s", self.model_path)
            return model
        except Exception:
            self.logger.exception("Failed to load YOLO model: %s", self.model_path)
            raise

    def detect(self, frame: np.ndarray, conf: float = 0.35) -> List[Detection]:
        if frame is None or frame.size == 0:
            return []

        resized = cv2.resize(frame, (640, 384), interpolation=cv2.INTER_AREA)
        results = self.model.predict(
            source=resized,
            conf=conf,
            verbose=False,
            imgsz=640,
            device="cpu",
        )

        detections: List[Detection] = []
        for result in results:
            names = result.names
            for box in result.boxes:
                class_id = int(box.cls.item())
                label = names[class_id]
                if label not in self.INTEREST_CLASSES:
                    continue
                label = self.NORMALIZED_NAMES.get(label, label)
                confidence = float(box.conf.item())
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
                detections.append(
                    Detection(
                        label=label,
                        confidence=confidence,
                        box=[x1, y1, x2, y2],
                    )
                )

        return detections
