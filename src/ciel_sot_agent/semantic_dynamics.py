"""Information dynamics: Hamiltonian H, Kuramoto step on TSM, timeline vector.

Faza 4 of the CIEL orbital architecture.

Three functions form the core:
  compute_H        — H_kinetic + H_potential + H_attractor (no arbitrary thresholds)
  kuramoto_step_tsm — one Kuramoto nudge on top-N TSM nodes, persists phi_berry
  append_timeline  — sliding-window timeline.json (max 500 entries)

Called from noema_sot.run() after nonlocal graph rebuild.
"""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

# ── paths ─────────────────────────────────────────────────────────────────────

_ROOT = resolve_project_root(__file__)
_TSM_DB = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"
_NONLOCAL_DB = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/nonlocal_graph.db"
_TIMELINE_PATH = _ROOT / "integration/registries/timeline.json"

_TIMELINE_MAX = 500
_NUDGE = 0.1  # Kuramoto coupling coefficient — protects against fast phase drift


# ── Hamiltonian ────────────────────────────────────────────────────────────────

def compute_H(
    phi_arr: list[float],
    winding_arr: list[float],
    edges: list[tuple[str, str, float]],      # (src_idx, dst_idx, weight) — indices into phi_arr
    node_ids: list[str],
    delta_t: float,
    phi_prev: list[float] | None = None,
) -> dict[str, Any]:
    """Compute H = H_kinetic + H_potential + H_attractor.

    H_kinetic  = (1/2) Σ m_i · ω_i²        mass = winding_n / max(winding_n)
    H_potential = -Σ W_ij · cos(φ_i - φ_j)  minimum when phases align
    H_attractor = Σ m_i · (-log(1 - ρ_i²))  Poincaré disk metric (ρ = tanh(|φ|/π))

    dH_dt estimated from phi_prev if provided.
    """
    n = len(phi_arr)
    if n == 0:
        return {"H_kinetic": 0.0, "H_potential": 0.0, "H_attractor": 0.0,
                "H_total": 0.0, "dH_dt": 0.0, "n_nodes": 0}

    max_w = max(winding_arr) if winding_arr else 1.0
    if max_w == 0:
        max_w = 1.0
    masses = [w / max_w for w in winding_arr]

    # H_kinetic — angular velocity from phase difference (or zero if no history)
    if phi_prev and len(phi_prev) == n and delta_t > 0:
        omegas = [(phi_arr[i] - phi_prev[i]) / delta_t for i in range(n)]
    else:
        omegas = [0.0] * n
    H_kinetic = 0.5 * sum(masses[i] * omegas[i] ** 2 for i in range(n))

    # H_potential — build index from node_id → index
    id_to_idx = {nid: i for i, nid in enumerate(node_ids)}
    H_potential = 0.0
    for src, dst, w in edges:
        i = id_to_idx.get(src)
        j = id_to_idx.get(dst)
        if i is not None and j is not None and i != j:
            H_potential -= w * math.cos(phi_arr[i] - phi_arr[j])

    # H_attractor — hyperbolic Poincaré disk metric -log(1-ρ²)
    # ρ = tanh(|φ|/π) ∈ [0, 1) always safe
    H_attractor = 0.0
    for i in range(n):
        rho = math.tanh(abs(phi_arr[i]) / math.pi)
        rho = min(rho, 0.9999)  # numerical guard at boundary
        H_attractor += masses[i] * (-math.log(1.0 - rho * rho))

    H_total = H_kinetic + H_potential + H_attractor

    # dH_dt — placeholder; caller computes from timeline delta
    dH_dt = 0.0

    return {
        "H_kinetic":   round(H_kinetic, 6),
        "H_potential": round(H_potential, 6),
        "H_attractor": round(H_attractor, 6),
        "H_total":     round(H_total, 6),
        "dH_dt":       dH_dt,
        "n_nodes":     n,
    }


# ── Kuramoto step on TSM ───────────────────────────────────────────────────────

def kuramoto_step_tsm(root: Path, delta_t: float = 0.006, N: int = 200) -> dict[str, Any]:
    """One Kuramoto nudge on top-N TSM nodes (by winding_n), update phi_berry in DB.

    Uses nonlocal_graph.db for edge weights (W_ij).
    Natural frequency ω_i comes from winding_n heterogeneity (Lorentz-inspired):
        ω_i = (winding_n_i / max_w - 0.5) * π   ← spreads in (-π/2, π/2)

    Nudge: φ_new = φ_old + NUDGE · delta_t · (ω_i + Σ_j W_ij · sin(φ_j - φ_i))
    """
    result: dict[str, Any] = {
        "updated": 0, "H": {}, "r_sync": 0.0, "error": None
    }

    if not _TSM_DB.exists():
        result["error"] = "TSM DB not found"
        return result

    # Load top-N TSM nodes
    try:
        tsm_con = sqlite3.connect(str(_TSM_DB))
        rows = tsm_con.execute(
            "SELECT memorise_id, phi_berry, winding_n FROM memories "
            "WHERE phi_berry IS NOT NULL AND winding_n IS NOT NULL "
            "ORDER BY winding_n DESC LIMIT ?",
            (N,)
        ).fetchall()
    except Exception as exc:
        result["error"] = f"TSM read error: {exc}"
        return result

    if not rows:
        result["error"] = "No TSM nodes with phi_berry"
        return result

    node_ids  = [r[0] for r in rows]
    phi_old   = [float(r[1]) for r in rows]
    winding   = [float(r[2]) if r[2] is not None else 1.0 for r in rows]
    id_to_idx = {nid: i for i, nid in enumerate(node_ids)}

    # Load edges from nonlocal_graph.db
    edges: list[tuple[str, str, float]] = []
    if _NONLOCAL_DB.exists():
        try:
            nl_con = sqlite3.connect(str(_NONLOCAL_DB))
            node_set = set(node_ids)
            edge_rows = nl_con.execute(
                "SELECT src, dst, weight FROM nonlocal_edges"
            ).fetchall()
            edges = [(s, d, float(w)) for s, d, w in edge_rows
                     if s in node_set and d in node_set]
            nl_con.close()
        except Exception:
            pass

    # Natural frequencies — heterogeneity from winding_n (Lorentz-inspired)
    max_w = max(winding) if winding else 1.0
    if max_w == 0:
        max_w = 1.0
    omegas = [(w / max_w - 0.5) * math.pi for w in winding]

    # Build adjacency for Kuramoto sum
    n = len(node_ids)
    adj: dict[int, list[tuple[int, float]]] = {i: [] for i in range(n)}
    for src, dst, w in edges:
        i = id_to_idx.get(src)
        j = id_to_idx.get(dst)
        if i is not None and j is not None:
            adj[i].append((j, w))

    # Kuramoto step
    dphi = []
    for i in range(n):
        coupling_sum = sum(w * math.sin(phi_old[j] - phi_old[i]) for j, w in adj[i])
        dphi.append(delta_t * (omegas[i] + coupling_sum))

    phi_new = [phi_old[i] + _NUDGE * dphi[i] for i in range(n)]

    # Kuramoto order parameter r·e^{iΨ}
    r_x = sum(math.cos(p) for p in phi_new) / n
    r_y = sum(math.sin(p) for p in phi_new) / n
    r_sync = round(math.sqrt(r_x * r_x + r_y * r_y), 5)

    # Persist updated phi_berry to TSM
    ts_now = datetime.now(timezone.utc).isoformat()
    updated = 0
    try:
        for i, nid in enumerate(node_ids):
            tsm_con.execute(
                "UPDATE memories SET phi_berry = ?, holonomy_ts = ? WHERE memorise_id = ?",
                (phi_new[i], ts_now, nid)
            )
            updated += 1
        tsm_con.commit()
    except Exception as exc:
        result["error"] = f"TSM write error: {exc}"
    finally:
        tsm_con.close()

    result["updated"] = updated

    # Compute H with new phases
    H = compute_H(phi_new, winding, edges, node_ids, delta_t, phi_old)
    result["H"] = H
    result["r_sync"] = r_sync

    return result


# ── Timeline ───────────────────────────────────────────────────────────────────

def append_timeline(
    root: Path,
    cycle_index: int | float,
    pipeline: dict[str, Any],
    H: dict[str, Any],
    prev_H_total: float | None = None,
) -> None:
    """Append one entry to timeline.json; keep sliding window of _TIMELINE_MAX."""
    _TIMELINE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if _TIMELINE_PATH.exists():
        try:
            doc = json.loads(_TIMELINE_PATH.read_text(encoding="utf-8"))
        except Exception:
            doc = {"entries": []}
    else:
        doc = {"entries": []}

    entries: list[dict] = doc.get("entries", [])

    # dH_dt from previous H_total in timeline
    dH_dt = None
    if prev_H_total is not None and H.get("H_total") is not None:
        dH_dt = round(H["H_total"] - prev_H_total, 6)
    elif entries:
        last_H = entries[-1].get("H", {}).get("H_total")
        if last_H is not None and H.get("H_total") is not None:
            dH_dt = round(float(H["H_total"]) - float(last_H), 6)

    entry = {
        "t":             int(cycle_index),
        "ts":            datetime.now(timezone.utc).isoformat(),
        "identity_phase":pipeline.get("identity_phase"),
        "tags":          _extract_pipeline_tags(pipeline),
        "phi_mean":      round(pipeline.get("phi_mean", 0.0) or 0.0, 5),
        "coherence":     pipeline.get("coherence_index"),
        "health":        pipeline.get("system_health"),
        "closure":       pipeline.get("closure_penalty"),
        "emotion":       pipeline.get("dominant_emotion"),
        "gate_mode":     pipeline.get("gate_mode"),
        "H":             {k: v for k, v in H.items() if k != "dH_dt"},
        "dH_dt":         dH_dt,
        "r_sync":        H.get("r_sync"),
    }
    # Remove None values to keep file lean
    entry = {k: v for k, v in entry.items() if v is not None}

    entries.append(entry)

    # Sliding window
    if len(entries) > _TIMELINE_MAX:
        entries = entries[-_TIMELINE_MAX:]

    doc["entries"] = entries
    doc["last_updated"] = datetime.now(timezone.utc).isoformat()
    doc["count"] = len(entries)

    _TIMELINE_PATH.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _extract_pipeline_tags(pipeline: dict[str, Any]) -> list[str]:
    """Derive semantic tags from pipeline state (no thresholds — presence-based)."""
    tags = []
    if pipeline.get("gate_mode") == "deep":
        tags.append("deep")
    if pipeline.get("gate_mode") == "safe":
        tags.append("safe")
    if pipeline.get("dominant_emotion"):
        tags.append(str(pipeline["dominant_emotion"]))
    # Tag active subsystems from available keys
    for key, tag in [
        ("closure_defect", "sync"),
        ("coherence_index", "bridge"),
        ("ethical_score", "omega"),
        ("soul_invariant", "identity"),
        ("entity_count", "entities"),
    ]:
        if pipeline.get(key) is not None:
            tags.append(tag)
    return tags


# ── Last H_total from timeline (for dH_dt) ────────────────────────────────────

def last_H_total() -> float | None:
    """Read H_total from the last timeline entry."""
    if not _TIMELINE_PATH.exists():
        return None
    try:
        doc = json.loads(_TIMELINE_PATH.read_text(encoding="utf-8"))
        entries = doc.get("entries", [])
        if entries:
            return entries[-1].get("H", {}).get("H_total")
    except Exception:
        pass
    return None
