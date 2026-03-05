"""Risk classification from detected objects."""
from __future__ import annotations

from typing import Dict


class RiskClassifier:
    """Combine distance, direction, and motion into risk level."""

    def classify(self, obj: Dict) -> str:
        score = 0
        if obj.get("distance_class") == "DANGER":
            score += 3
        elif obj.get("distance_class") == "CAUTION":
            score += 2

        if obj.get("direction") == "center":
            score += 2
        else:
            score += 1

        if obj.get("moving"):
            score += 2

        if score >= 6:
            return "HIGH"
        if score >= 4:
            return "MEDIUM"
        return "LOW"
