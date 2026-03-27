from __future__ import annotations
from datetime import datetime, timezone

def coherence_index_from_snapshot(final: dict) -> float:
    R_H = float(final.get("R_H", 1.0))
    return max(0.0, min(1.0, 1.0 - R_H))

def topological_charge_global(final: dict) -> float:
    return float(final.get("Lambda_glob", 0.0))

def phase_lock_error(final: dict) -> float:
    return float(final.get("closure_penalty", 0.0))

def recommend_control(final: dict) -> dict:
    ci = coherence_index_from_snapshot(final)
    err = phase_lock_error(final)
    if ci < 0.82 or err > 5.8:
        mode = "safe"
        notes = "Low coherence or high closure penalty: use conservative execution."
        dt_override = 0.018
        zeta_scale = 0.30
    elif ci < 0.90 or err > 5.2:
        mode = "standard"
        notes = "Stable but not deep-merge safe."
        dt_override = 0.0205
        zeta_scale = 0.35
    else:
        mode = "deep"
        notes = "Strong coherence: allow deeper diagnostic/integration passes."
        dt_override = 0.022
        zeta_scale = 0.38
    zeta_phase = float(final.get("zeta_effective_phase", 0.0) or 0.0)
    return {
        "mode": mode,
        "phase_lock_enable": True,
        "target_phase_shift": -zeta_phase,
        "dt_override": dt_override,
        "zeta_coupling_scale": zeta_scale,
        "mu_phi": 0.18 if mode != "safe" else 0.16,
        "epsilon_hom": 0.22 if mode != "safe" else 0.18,
        "notes": notes,
    }

def build_state_manifest(final: dict) -> dict:
    return {
        "coherence_index": coherence_index_from_snapshot(final),
        "topological_charge_global": topological_charge_global(final),
        "phase_lock_error": phase_lock_error(final),
        "beat_frequency_target_hz": 7.83,
        "spectral_radius_A": float(final.get("spectral_radius_A", 0.0)),
        "fiedler_L": float(final.get("fiedler_L", 0.0)),
        "zeta_enabled": bool(final.get("zeta_enabled", False)),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def build_health_manifest(final: dict) -> dict:
    ci = coherence_index_from_snapshot(final)
    err = phase_lock_error(final)
    health = max(0.0, min(1.0, ci / (1.0 + 0.1 * err)))
    if health < 0.25:
        risk = "high"
        action = "read-only only; run diagnostics and avoid write-back"
    elif health < 0.5:
        risk = "medium"
        action = "standard mode; capture extra reports"
    else:
        risk = "low"
        action = "deep diagnostics allowed"
    return {
        "system_health": health,
        "risk_level": risk,
        "closure_penalty": float(final.get("closure_penalty", 0.0)),
        "R_H": float(final.get("R_H", 0.0)),
        "T_glob": float(final.get("T_glob", 0.0)),
        "Lambda_glob": float(final.get("Lambda_glob", 0.0)),
        "recommended_action": action,
    }
