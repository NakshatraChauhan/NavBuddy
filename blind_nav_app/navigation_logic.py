import time
from typing import Dict, List, Optional


class NavigationAdvisor:
    def __init__(self):
        self.last_warning = ""
        self.last_warning_at = 0.0
        self.cooldown_s = 2.5

    def _closest(self, detections: List[Dict]) -> Optional[Dict]:
        if not detections:
            return None
        return sorted(detections, key=lambda d: d.get("distance_m", 99))[0]

    def _direction_hint(self, direction: str) -> str:
        if direction == "Center":
            return "Move slightly to your left if possible."
        if direction == "Left":
            return "Move a little right."
        return "Move a little left."

    def guidance(self, detections: List[Dict]) -> Dict:
        closest = self._closest(detections)
        if not closest:
            return {
                "warning": False,
                "priority_obstacle": None,
                "message": "Path ahead is clear. Walk forward.",
            }

        label = closest["label"]
        distance = closest["distance_m"]
        direction = closest["direction"]
        severity = closest.get("distance_label", "Safe")

        if severity == "Safe":
            return {
                "warning": False,
                "priority_obstacle": closest,
                "message": f"{label.title()} detected on your {direction.lower()} at {distance} meters. Path mostly clear.",
            }

        message = (
            f"Warning. {label.title()} {('ahead' if direction == 'Center' else 'on your ' + direction.lower())} "
            f"{distance} meters. {self._direction_hint(direction)}"
        )

        now = time.time()
        should_alert = message != self.last_warning or now - self.last_warning_at > self.cooldown_s
        if should_alert:
            self.last_warning = message
            self.last_warning_at = now

        return {
            "warning": should_alert,
            "priority_obstacle": closest,
            "message": message,
        }
