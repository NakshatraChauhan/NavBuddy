"""Build weighted graph from OSM-like map JSON."""
from __future__ import annotations

from typing import Dict, Tuple

import networkx as nx

from utils.helpers import haversine_distance_m


class GraphBuilder:
    """Creates route graph for pathfinding."""

    def build(self, map_data: dict) -> Tuple[nx.Graph, Dict[str, tuple]]:
        graph = nx.Graph()
        node_map: Dict[str, tuple] = {}

        for node in map_data.get("nodes", []):
            nid = str(node["id"])
            coord = (node["lat"], node["lon"])
            node_map[nid] = coord
            graph.add_node(nid, lat=node["lat"], lon=node["lon"]) 

        for edge in map_data.get("edges", []):
            src = str(edge["source"])
            dst = str(edge["target"])
            if src not in node_map or dst not in node_map:
                continue
            dist = haversine_distance_m(*node_map[src], *node_map[dst])
            graph.add_edge(src, dst, weight=dist)

        return graph, node_map
