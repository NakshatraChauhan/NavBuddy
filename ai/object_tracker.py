"""Simple object tracker built on nearest-center association."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Track:
    track_id: int
    center: Tuple[float, float]
    label: str


class ObjectTracker:
    """Maintain stable IDs for detections across frames."""

    def __init__(self, max_distance: float = 60.0) -> None:
        self.max_distance = max_distance
        self.next_id = 1
        self.tracks: Dict[int, Track] = {}

    def update(self, detections: List[dict]) -> List[dict]:
        updated = {}
        output = []

        for det in detections:
            cx, cy = det["center"]
            label = det["label"]
            assigned_id = None
            best_dist = self.max_distance
            for tid, tr in self.tracks.items():
                if tr.label != label:
                    continue
                dist = ((cx - tr.center[0]) ** 2 + (cy - tr.center[1]) ** 2) ** 0.5
                if dist < best_dist:
                    assigned_id = tid
                    best_dist = dist
            if assigned_id is None:
                assigned_id = self.next_id
                self.next_id += 1

            updated[assigned_id] = Track(assigned_id, (cx, cy), label)
            det["track_id"] = assigned_id
            output.append(det)

        self.tracks = updated
        return output
