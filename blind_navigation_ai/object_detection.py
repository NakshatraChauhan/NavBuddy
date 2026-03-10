from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Dict, List, Optional

import cv2
import numpy as np
from PIL import Image

NAV_CLASSES = {
    "person",
    "chair",
    "table",
    "cell phone",
    "car",
    "bicycle",
    "dog",
    "bench",
    "backpack",
}


@dataclass
class Detection:
    label: str
    confidence: float
    bbox: List[int]
    center: List[int]


class ObjectDetector:
    def __init__(self, model_path: str = "models/yolov8n.pt"):
        self.model_path = model_path
        self.model = None
        self.class_names: Dict[int, str] = {}
        self.using_fallback = False
        self._load_model()

    def _load_model(self) -> None:
        try:
            from ultralytics import YOLO

            self.model = YOLO(self.model_path)
            self.class_names = self.model.names
        except Exception:
            self.model = None
            self.using_fallback = True

    @staticmethod
    def decode_frame(frame_b64: str) -> np.ndarray:
        frame_bytes = base64.b64decode(frame_b64.split(",")[-1])
        img = Image.open(io.BytesIO(frame_bytes)).convert("RGB")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def _fallback_detect(self, frame: np.ndarray) -> List[Detection]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 70, 160)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h, w = frame.shape[:2]
        min_area = 0.015 * h * w
        detections: List[Detection] = []
        for c in sorted(contours, key=cv2.contourArea, reverse=True)[:6]:
            if cv2.contourArea(c) < min_area:
                continue
            x, y, cw, ch = cv2.boundingRect(c)
            detections.append(
                Detection(
                    label="obstacle",
                    confidence=0.45,
                    bbox=[int(x), int(y), int(x + cw), int(y + ch)],
                    center=[int(x + cw / 2), int(y + ch / 2)],
                )
            )
        return detections

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if self.model is None:
            return self._fallback_detect(frame)

        result = self.model.predict(frame, conf=0.35, imgsz=640, verbose=False)[0]
        detections: List[Detection] = []
        for box in result.boxes:
            cls_id = int(box.cls.item())
            label = self.class_names.get(cls_id, "unknown")
            if label not in NAV_CLASSES:
                continue
            conf = float(box.conf.item())
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            detections.append(
                Detection(
                    label=label,
                    confidence=round(conf, 3),
                    bbox=[x1, y1, x2, y2],
                    center=[int((x1 + x2) / 2), int((y1 + y2) / 2)],
                )
            )
        return detections
