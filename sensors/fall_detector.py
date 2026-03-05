"""Fall detection using acceleration thresholds."""
from __future__ import annotations


class FallDetector:
    """Detect a potential fall event from acceleration spike + drop."""

    def __init__(self) -> None:
        self.last_high = False

    def detect(self, magnitude: float) -> bool:
        if magnitude > 20:
            self.last_high = True
            return False
        if self.last_high and magnitude < 5:
            self.last_high = False
            return True
        if magnitude > 8:
            self.last_high = False
        return False
