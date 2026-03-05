"""OSM JSON parser module."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class OSMParser:
    """Parse compact map data with nodes and edges."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, List[dict]]:
        if not self.path.exists():
            raise FileNotFoundError(f"Map data not found: {self.path}")
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
