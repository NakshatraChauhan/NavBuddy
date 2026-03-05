"""GPS location handling module."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Location:
    lat: float
    lon: float


class GPSManager:
    """Manage location updates and validation."""

    def __init__(self) -> None:
        self.current = Location(lat=0.0, lon=0.0)

    def update(self, lat: float, lon: float) -> Location:
        self.current = Location(lat=float(lat), lon=float(lon))
        return self.current

    def get_current(self) -> Location:
        return self.current
