"""Motion state inference from browser motion payloads."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MotionState:
    walking: bool
    sudden_stop: bool
    orientation: str


class MotionDetection:
    """Infer walking and abrupt stop events from acceleration history."""

    def __init__(self) -> None:
        self.prev_magnitude = 0.0

    def analyze(self, ax: float, ay: float, az: float, orientation: str) -> MotionState:
        magnitude = (ax ** 2 + ay ** 2 + az ** 2) ** 0.5
        walking = 9.8 < magnitude < 14.0
        sudden_stop = self.prev_magnitude > 12.0 and magnitude < 9.5
        self.prev_magnitude = magnitude
        return MotionState(walking=walking, sudden_stop=sudden_stop, orientation=orientation)
