"""Distance estimation using monocular bounding-box scaling."""
from __future__ import annotations

from dataclasses import dataclass


REAL_HEIGHT_M = {
    "person": 1.7,
    "car": 1.5,
    "bicycle": 1.1,
    "motorcycle": 1.2,
    "chair": 1.0,
    "table": 0.8,
    "traffic light": 3.0,
    "door": 2.0,
    "stairs": 1.5,
    "wall": 2.5,
}


@dataclass
class DistanceEstimate:
    distance_m: float
    distance_class: str


class DistanceEstimator:
    """Compute object distance and safety classes."""

    def __init__(self, focal_length_px: float) -> None:
        self.focal_length_px = focal_length_px

    def estimate(self, label: str, box_height: float) -> DistanceEstimate:
        real_h = REAL_HEIGHT_M.get(label, 1.5)
        box_height = max(box_height, 1.0)
        distance = (self.focal_length_px * real_h) / box_height

        if distance < 1.5:
            dclass = "DANGER"
        elif distance < 3.5:
            dclass = "CAUTION"
        else:
            dclass = "SAFE"

        return DistanceEstimate(distance_m=round(distance, 2), distance_class=dclass)
