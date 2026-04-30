"""Load geometric data from CIEL integration layer JSON/YAML files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml
    _YAML_OK = True
except ImportError:
    _YAML_OK = False

# Base path: src/ciel_geometry/ → project root → integration/
_INTEGRATION = Path(__file__).parent.parent.parent / "integration"


@dataclass
class SectorGeom:
    name: str
    theta: float
    phi: float
    amplitude: float
    coherence_weight: float
    info_mass: float
    orbital_type: str
    dominant_spin: str
    tau: float
    defect: float = 0.02


@dataclass
class EntityGeom:
    id: str
    noun: str
    coupling_ciel: float  # used as rho on Poincaré disk
    phase: float          # used as phi angle
    horizon_class: str
    adjectives: list[str] = field(default_factory=list)
    note: str = ""


@dataclass
class BridgeState:
    coherence_index: float
    system_health: float
    closure_penalty: float
    mode: str
    phase_lock_error: float
    timestamp: str = ""


def load_sectors(path: Optional[Path] = None) -> dict[str, SectorGeom]:
    p = path or (_INTEGRATION / "Orbital/main/manifests/sectors_global.json")
    raw = json.loads(p.read_text())
    result: dict[str, SectorGeom] = {}
    for name, s in raw.get("sectors", {}).items():
        result[name] = SectorGeom(
            name=name,
            theta=float(s["theta"]),
            phi=float(s["phi"]),
            amplitude=float(s.get("amplitude", 1.0)),
            coherence_weight=float(s.get("coherence_weight", 1.0)),
            info_mass=float(s.get("info_mass", 1.0)),
            orbital_type=s.get("orbital_type", "S"),
            dominant_spin=s.get("dominant_spin", ""),
            tau=float(s.get("tau", 0.353)),
            defect=float(s.get("defect", 0.02)),
        )
    return result


def load_couplings(path: Optional[Path] = None) -> dict[tuple[str, str], float]:
    p = path or (_INTEGRATION / "Orbital/main/manifests/couplings_global.json")
    raw = json.loads(p.read_text())
    result: dict[tuple[str, str], float] = {}
    for src, targets in raw.get("couplings", {}).items():
        for dst, w in targets.items():
            result[(src, dst)] = float(w)
            if (dst, src) not in result:
                result[(dst, src)] = float(w)
    return result


def load_entities(path: Optional[Path] = None) -> list[EntityGeom]:
    p = path or (_INTEGRATION / "registries/ciel_entity_cards.yaml")
    if not _YAML_OK:
        raise ImportError("PyYAML is required for load_entities(). Install with: pip install pyyaml")
    raw = yaml.safe_load(p.read_text())
    result: list[EntityGeom] = []
    for e in raw.get("entities", []):
        result.append(EntityGeom(
            id=e["id"],
            noun=e.get("noun", e["id"]),
            coupling_ciel=float(e.get("coupling_ciel", 0.5)),
            phase=float(e.get("phase", 0.0)),
            horizon_class=e.get("horizon_class", "POROUS"),
            adjectives=e.get("adjectives", []),
            note=e.get("note", ""),
        ))
    return result


def load_bridge_state(path: Optional[Path] = None) -> BridgeState:
    p = path or (_INTEGRATION / "reports/orbital_bridge/orbital_bridge_report.json")
    raw = json.loads(p.read_text())

    state = raw.get("state_manifest", raw)
    health = raw.get("health_manifest", raw)
    ctrl = raw.get("recommended_control", {})

    return BridgeState(
        coherence_index=float(state.get("coherence_index", health.get("coherence_index", 0.9))),
        system_health=float(health.get("system_health", state.get("system_health", 0.6))),
        closure_penalty=float(health.get("closure_penalty", state.get("closure_penalty", 4.6))),
        mode=ctrl.get("mode", health.get("mode", "standard")),
        phase_lock_error=float(state.get("phase_lock_error", health.get("phase_lock_error", 0.0))),
        timestamp=raw.get("timestamp", ""),
    )
