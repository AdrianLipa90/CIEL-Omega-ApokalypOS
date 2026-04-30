"""Build geodesic edges between nodes on the Poincaré disk."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .disk import geodesic_arc


# Weight threshold below which we skip drawing an edge
_MIN_WEIGHT = 0.05


@dataclass
class GeodesicEdge:
    src: str
    dst: str
    weight: float
    arc_points: list[tuple[float, float]]


def build_sector_edges(
    sector_positions: dict[str, tuple[float, float]],
    couplings: dict[tuple[str, str], float],
    min_weight: float = _MIN_WEIGHT,
) -> list[GeodesicEdge]:
    """Build geodesic edges between sectors using coupling matrix."""
    edges: list[GeodesicEdge] = []
    seen: set[frozenset[str]] = set()

    for (src, dst), w in couplings.items():
        key = frozenset({src, dst})
        if key in seen or w < min_weight:
            continue
        if src not in sector_positions or dst not in sector_positions:
            continue
        seen.add(key)
        x1, y1 = sector_positions[src]
        x2, y2 = sector_positions[dst]
        arc = geodesic_arc(x1, y1, x2, y2)
        edges.append(GeodesicEdge(src=src, dst=dst, weight=w, arc_points=arc))

    return edges


def build_entity_edges(
    entity_positions: dict[str, tuple[float, float]],
    sector_positions: dict[str, tuple[float, float]],
    entity_sectors: Optional[dict[str, str]] = None,
    min_weight: float = 0.3,
) -> list[GeodesicEdge]:
    """Build edges from entities to their owning sector (if sector mapping provided)."""
    if not entity_sectors:
        return []

    edges: list[GeodesicEdge] = []
    for eid, sector_name in entity_sectors.items():
        if eid not in entity_positions or sector_name not in sector_positions:
            continue
        x1, y1 = entity_positions[eid]
        x2, y2 = sector_positions[sector_name]
        arc = geodesic_arc(x1, y1, x2, y2, steps=12)
        edges.append(GeodesicEdge(src=eid, dst=sector_name, weight=0.5, arc_points=arc))

    return edges
