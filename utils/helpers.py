"""Common utility helpers."""
from __future__ import annotations

import math
from datetime import datetime


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in meters."""
    radius = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def normalize_direction(x_center: float, frame_width: float) -> str:
    """Estimate rough direction (left/center/right) based on x coordinate."""
    ratio = x_center / max(frame_width, 1)
    if ratio < 0.33:
        return "left"
    if ratio > 0.66:
        return "right"
    return "center"
