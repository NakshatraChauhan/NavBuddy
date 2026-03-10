from __future__ import annotations

from typing import Dict, List


def direction_from_center(cx: int, frame_width: int) -> str:
    left = frame_width / 3
    right = 2 * frame_width / 3
    if cx < left:
        return "Left"
    if cx > right:
        return "Right"
    return "Center"


def combine_detections_with_depth(detections: List[Dict], depth_estimator, depth_map, frame_shape) -> List[Dict]:
    h, w = frame_shape[:2]
    enriched: List[Dict] = []
    for d in detections:
        cx, cy = d["center"]
        dist = depth_estimator.object_distance_m(depth_map, d["bbox"])
        enriched.append(
            {
                **d,
                "distance_m": dist,
                "distance_band": depth_estimator.distance_band(dist),
                "direction": direction_from_center(cx, w),
            }
        )
    return sorted(enriched, key=lambda x: x["distance_m"])


def scene_summary(objects: List[Dict]) -> str:
    if not objects:
        return "Path appears clear."
    parts = []
    for obj in objects[:4]:
        where = "ahead" if obj["direction"] == "Center" else f"on your {obj['direction'].lower()}"
        parts.append(f"{obj['label']} {where} at {obj['distance_m']} meters")
    return "I see " + ", ".join(parts) + "."
