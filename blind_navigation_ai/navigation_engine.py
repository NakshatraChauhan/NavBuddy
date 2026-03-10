from __future__ import annotations

import time
from typing import Dict, List


class NavigationEngine:
    def __init__(self, cooldown_s: float = 2.0):
        self.cooldown_s = cooldown_s
        self.last_message = ""
        self.last_at = 0.0

    def _blocked(self, objects: List[Dict], side: str) -> bool:
        for o in objects:
            if o["direction"] == side and o["distance_m"] <= 2.0:
                return True
        return False

    def decide(self, objects: List[Dict]) -> Dict:
        if not objects:
            msg = "Path clear. Walk forward."
            return {"message": msg, "speak": self._should_speak(msg), "action": "forward"}

        closest = objects[0]
        direction = closest["direction"]
        dist = closest["distance_m"]

        if direction == "Center" and dist <= 2.0:
            left_blocked = self._blocked(objects, "Left")
            right_blocked = self._blocked(objects, "Right")
            if left_blocked and right_blocked:
                msg = f"Stop. {closest['label']} ahead at {dist} meters."
                return {"message": msg, "speak": self._should_speak(msg), "action": "stop"}
            if left_blocked:
                msg = f"Obstacle ahead. Move slightly right. {closest['label']} at {dist} meters."
                return {"message": msg, "speak": self._should_speak(msg), "action": "right"}
            msg = f"Obstacle ahead. Move slightly left. {closest['label']} at {dist} meters."
            return {"message": msg, "speak": self._should_speak(msg), "action": "left"}

        if direction == "Left" and dist <= 2.0:
            msg = f"{closest['label'].title()} on your left at {dist} meters. Move right."
            return {"message": msg, "speak": self._should_speak(msg), "action": "right"}

        if direction == "Right" and dist <= 2.0:
            msg = f"{closest['label'].title()} on your right at {dist} meters. Move left."
            return {"message": msg, "speak": self._should_speak(msg), "action": "left"}

        msg = f"Safe path forward. Closest {closest['label']} at {dist} meters."
        return {"message": msg, "speak": self._should_speak(msg), "action": "forward"}

    def _should_speak(self, message: str) -> bool:
        now = time.time()
        if message != self.last_message or now - self.last_at > self.cooldown_s:
            self.last_message = message
            self.last_at = now
            return True
        return False
