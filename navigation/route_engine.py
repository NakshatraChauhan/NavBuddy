"""A* route engine with turn-by-turn instructions."""
from __future__ import annotations

from typing import Dict, List

import networkx as nx

from utils.helpers import haversine_distance_m


class RouteEngine:
    """Compute route and human-readable instructions."""

    def __init__(self, graph: nx.Graph, node_map: Dict[str, tuple]) -> None:
        self.graph = graph
        self.node_map = node_map

    def _nearest_node(self, lat: float, lon: float) -> str:
        return min(
            self.node_map,
            key=lambda nid: haversine_distance_m(lat, lon, self.node_map[nid][0], self.node_map[nid][1]),
        )

    def _heuristic(self, n1: str, n2: str) -> float:
        return haversine_distance_m(
            self.node_map[n1][0], self.node_map[n1][1], self.node_map[n2][0], self.node_map[n2][1]
        )

    def build_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> dict:
        start_node = self._nearest_node(start_lat, start_lon)
        end_node = self._nearest_node(end_lat, end_lon)

        path = nx.astar_path(self.graph, start_node, end_node, heuristic=self._heuristic, weight="weight")
        coords = [{"node": nid, "lat": self.node_map[nid][0], "lon": self.node_map[nid][1]} for nid in path]

        instructions: List[str] = []
        for idx in range(1, len(coords)):
            prev = coords[idx - 1]
            curr = coords[idx]
            dist = haversine_distance_m(prev["lat"], prev["lon"], curr["lat"], curr["lon"])
            turn = "Continue straight"
            if idx == len(coords) - 1:
                turn = "You have reached your destination"
            instructions.append(f"{turn} in {int(dist)} meters")

        return {"path": coords, "instructions": instructions}
