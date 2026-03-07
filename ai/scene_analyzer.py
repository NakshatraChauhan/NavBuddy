from __future__ import annotations

from collections import Counter
from typing import List

from ai.detector import Detection


class SceneAnalyzer:
    def __init__(self, logger) -> None:
        self.logger = logger

    @staticmethod
    def _position_for_detection(d: Detection, frame_width: int) -> str:
        center_x = (d.box[0] + d.box[2]) / 2
        left_bound = frame_width * 0.33
        right_bound = frame_width * 0.66

        if center_x < left_bound:
            return "left"
        if center_x > right_bound:
            return "right"
        return "ahead"

    def describe_scene(self, detections: List[Detection], frame_width: int) -> str:
        if not detections:
            return "No major obstacles detected. Path mostly clear."

        counts = Counter([d.label for d in detections])
        priority = ["person", "car", "bicycle", "motorcycle", "chair", "table", "door", "wall", "stairs"]
        selected_label = next((label for label in priority if counts.get(label)), None)

        if selected_label is None:
            selected_label = detections[0].label

        selected = [d for d in detections if d.label == selected_label]
        closest = max(selected, key=lambda d: d.confidence)
        position = self._position_for_detection(closest, frame_width)

        secondary = [label for label, count in counts.items() if label != selected_label and count > 0]
        if secondary:
            second = secondary[0]
            return f"{selected_label.capitalize()} {position}. {second.capitalize()} nearby. Proceed carefully."

        return f"{selected_label.capitalize()} {position}. Proceed carefully."

    def navigation_alert(self, detections: List[Detection], frame_width: int) -> str:
        if not detections:
            return "Path clear"

        high_priority = [d for d in detections if d.label in {"person", "car", "bicycle", "motorcycle"}]
        target = max(high_priority or detections, key=lambda d: d.confidence)
        position = self._position_for_detection(target, frame_width)

        if position == "ahead":
            return "Obstacle ahead"
        return f"Object on the {position}"
