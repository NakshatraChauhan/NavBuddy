from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


class DepthEstimator:
    """MiDaS depth estimator with robust fallback when torch/MiDaS is unavailable."""

    def __init__(self):
        self.midas = None
        self.transform = None
        self.device = "cpu"
        self.using_fallback = False
        self._load_midas()

    def _load_midas(self) -> None:
        try:
            import torch

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
            self.midas.to(self.device)
            self.midas.eval()
            transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            self.transform = transforms.small_transform
        except Exception:
            self.midas = None
            self.transform = None
            self.using_fallback = True

    def estimate_depth_map(self, frame: np.ndarray) -> np.ndarray:
        if self.midas is None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            norm = cv2.normalize(gray.astype(np.float32), None, 0.0, 1.0, cv2.NORM_MINMAX)
            return 1.0 - norm

        import torch

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_batch = self.transform(rgb).to(self.device)
        with torch.no_grad():
            prediction = self.midas(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
            depth = prediction.cpu().numpy()
            depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-6)
            return depth.astype(np.float32)

    @staticmethod
    def object_distance_m(depth_map: np.ndarray, bbox: List[int]) -> float:
        x1, y1, x2, y2 = bbox
        h, w = depth_map.shape[:2]
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w - 1, x2), min(h - 1, y2)
        roi = depth_map[y1:y2, x1:x2]
        if roi.size == 0:
            return 5.0
        median_depth = float(np.median(roi))
        dist = max(0.4, min(6.0, 6.5 - (median_depth * 6.0)))
        return round(dist, 2)

    @staticmethod
    def distance_band(distance_m: float) -> str:
        if distance_m < 1.0:
            return "Very Close"
        if distance_m <= 2.0:
            return "Close"
        return "Safe"
