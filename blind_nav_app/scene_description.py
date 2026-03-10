from collections import defaultdict
from typing import Dict, List


def build_scene_summary(detections: List[Dict]) -> str:
    if not detections:
        return "I do not detect major obstacles right now. The path appears clear."

    grouped = defaultdict(list)
    for d in detections:
        grouped[d["label"]].append(d)

    phrases = []
    for label, items in grouped.items():
        closest = sorted(items, key=lambda x: x.get("distance_m", 99))[0]
        direction = closest.get("direction", "Center").lower()
        distance = closest.get("distance_m", "unknown")
        ahead_text = "ahead" if direction == "center" else f"on your {direction}"
        phrases.append(f"{label} {ahead_text} at about {distance} meters")

    return "I can see " + ", and ".join(phrases) + "."
