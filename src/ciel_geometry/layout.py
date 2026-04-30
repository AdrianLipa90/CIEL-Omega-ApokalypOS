"""Build a complete Poincaré disk layout snapshot from live CIEL system state."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict

from .loader import load_sectors, load_couplings, load_entities, load_bridge_state
from .disk import sector_to_disk, entity_to_disk
from .edges import build_sector_edges, GeodesicEdge

# Horizon class → color hint (RGB 0-1 tuples, for renderer use)
_HORIZON_COLOR = {
    "SEALED":        (0.2, 0.2, 0.6),
    "POROUS":        (0.2, 0.6, 0.4),
    "TRANSMISSIVE":  (0.9, 0.8, 0.2),
    "OBSERVATIONAL": (0.5, 0.5, 0.5),
}

_ORBITAL_TYPE_SHAPE = {"S": "circle", "F": "diamond", "P": "square"}


@dataclass
class DiskNode:
    id: str
    label: str
    x: float
    y: float
    size: float          # normalized [0, 1]
    color: tuple[float, float, float]
    node_type: str       # "sector" | "entity"
    shape: str           # "circle" | "diamond" | "square"
    horizon_class: str
    meta: dict = field(default_factory=dict)


@dataclass
class DiskEdge:
    src: str
    dst: str
    weight: float
    arc_points: list[tuple[float, float]]


@dataclass
class DiskLayout:
    nodes: list[DiskNode]
    edges: list[DiskEdge]
    metadata: dict

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, default=str)


def build_layout(
    include_entities: bool = True,
    entity_limit: int = 40,
) -> DiskLayout:
    """Build a complete Poincaré disk layout from live CIEL integration data."""
    sectors = load_sectors()
    couplings = load_couplings()
    bridge = load_bridge_state()

    nodes: list[DiskNode] = []
    sector_positions: dict[str, tuple[float, float]] = {}

    # --- Sector nodes ---
    for name, s in sectors.items():
        x, y = sector_to_disk(s.theta, s.phi)
        sector_positions[name] = (x, y)
        color = (0.3, 0.6, 0.9)  # default sector color
        shape = _ORBITAL_TYPE_SHAPE.get(s.orbital_type, "circle")
        size = min(1.0, s.amplitude * s.coherence_weight)
        nodes.append(DiskNode(
            id=f"sector:{name}",
            label=name,
            x=x, y=y,
            size=size,
            color=color,
            node_type="sector",
            shape=shape,
            horizon_class="POROUS",
            meta={
                "orbital_type": s.orbital_type,
                "dominant_spin": s.dominant_spin,
                "info_mass": s.info_mass,
                "tau": s.tau,
                "theta": s.theta,
                "phi": s.phi,
            },
        ))

    # --- Entity nodes ---
    entity_positions: dict[str, tuple[float, float]] = {}
    if include_entities:
        try:
            entities = load_entities()
        except (ImportError, FileNotFoundError):
            entities = []

        for e in entities[:entity_limit]:
            x, y = entity_to_disk(e.coupling_ciel, e.phase)
            entity_positions[e.id] = (x, y)
            color = _HORIZON_COLOR.get(e.horizon_class, (0.5, 0.5, 0.5))
            nodes.append(DiskNode(
                id=e.id,
                label=e.noun,
                x=x, y=y,
                size=e.coupling_ciel,
                color=color,
                node_type="entity",
                shape="circle",
                horizon_class=e.horizon_class,
                meta={"adjectives": e.adjectives[:3]},
            ))

    # --- Edges (sector couplings) ---
    geo_edges = build_sector_edges(sector_positions, couplings)
    edges = [DiskEdge(src=e.src, dst=e.dst, weight=e.weight, arc_points=e.arc_points) for e in geo_edges]

    metadata = {
        "coherence_index": bridge.coherence_index,
        "system_health": bridge.system_health,
        "closure_penalty": bridge.closure_penalty,
        "mode": bridge.mode,
        "phase_lock_error": bridge.phase_lock_error,
        "timestamp": bridge.timestamp,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }

    return DiskLayout(nodes=nodes, edges=edges, metadata=metadata)


if __name__ == "__main__":
    layout = build_layout()
    print(layout.to_json())
