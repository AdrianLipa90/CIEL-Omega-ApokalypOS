from __future__ import annotations
from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT / "systems" / "CIEL_OMEGA_COMPLETE_SYSTEM") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "systems" / "CIEL_OMEGA_COMPLETE_SYSTEM"))

from ciel_omega.orbital.global_pass import run_global_pass  # type: ignore

def _load_geometry() -> dict:
    path = REPO_ROOT / "reports" / "global_orbital_coherence_pass" / "real_geometry.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    run_global_pass()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def _load_summary() -> dict:
    path = REPO_ROOT / "reports" / "global_orbital_coherence_pass" / "summary.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return run_global_pass()

def get_topological_charge(node_id: str) -> float:
    geom = _load_geometry()
    centrality = geom.get("centrality", {})
    return float(centrality.get(node_id, 0.0))

def get_coherence_index(node_id: str | None = None) -> float:
    summary = _load_summary()
    final = summary.get("final", {})
    R_H = float(final.get("R_H", 1.0))
    base = max(0.0, 1.0 - R_H)
    if node_id is None:
        return base
    geom = _load_geometry()
    sectors = geom.get("sectors", {}).get("sectors", {})
    local = sectors.get(node_id, {})
    weight = float(local.get("coherence_weight", 1.0))
    return max(0.0, min(1.0, base * weight))

def get_phase(node_id: str) -> float:
    geom = _load_geometry()
    sectors = geom.get("sectors", {}).get("sectors", {})
    return float(sectors.get(node_id, {}).get("phase", 0.0))

def get_loop_integrity(loop_id: str | None = None) -> float:
    summary = _load_summary()
    final = summary.get("final", {})
    closure = float(final.get("closure_penalty", 0.0))
    return 1.0 / (1.0 + closure)

def sync_to_phase(target_phase: float) -> dict:
    summary = _load_summary()
    final = summary.get("final", {})
    current = float(final.get("zeta_effective_phase", 0.0) or 0.0)
    return {
        "current_phase": current,
        "target_phase": float(target_phase),
        "delta_phase": float(target_phase) - current,
        "recommended": "apply via control manifest; read-only API does not mutate runtime",
    }
