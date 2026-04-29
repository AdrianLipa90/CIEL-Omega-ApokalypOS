from __future__ import annotations
from datetime import datetime, timezone
import math

from .rh_control import RHController, effective_rh


def _obs(final: dict, *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if key in final and final.get(key) is not None:
            try:
                return float(final.get(key, default) or 0.0)
            except Exception:
                continue
    return float(default)


def coherence_index_from_snapshot(final: dict) -> float:
    raw = max(0.0, min(1.0, 1.0 - _obs(final, "R_H", default=1.0)))
    coherent_fraction = max(0.0, min(1.0, _obs(final, "nonlocal_coherent_fraction", "coherent_fraction")))
    eba_defect = max(0.0, min(1.0, _obs(final, "nonlocal_eba_defect_mean", "eba_defect_mean")))
    closure_score = max(0.0, min(1.0, _obs(final, "euler_bridge_closure_score", "bridge_closure_score", "closure_score")))
    ci = 0.55 * raw + 0.20 * coherent_fraction + 0.15 * (1.0 - eba_defect) + 0.10 * closure_score
    return max(0.0, min(1.0, ci))


def topological_charge_global(final: dict) -> float:
    return float(final.get("Lambda_glob", 0.0))


def phase_lock_error(final: dict) -> float:
    return float(final.get("closure_penalty", 0.0))


def recommend_control(final: dict) -> dict:
    ci = coherence_index_from_snapshot(final)
    err = phase_lock_error(final)
    coherent_fraction = max(0.0, min(1.0, _obs(final, "nonlocal_coherent_fraction", "coherent_fraction")))
    eba_defect = max(0.0, _obs(final, "nonlocal_eba_defect_mean", "eba_defect_mean"))
    closure_score = max(0.0, min(1.0, _obs(final, "euler_bridge_closure_score", "bridge_closure_score", "closure_score")))
    target_phase = _obs(final, "euler_bridge_target_phase", "bridge_target_phase", "target_phase")
    phi_berry = _obs(final, "nonlocal_phi_berry_mean", "phi_berry_mean")
    diff = (phi_berry - target_phase + math.pi) % (2 * math.pi) - math.pi
    phase_gap = min(1.0, abs(diff) / math.pi)

    rh_decision = RHController().evaluate_snapshot(final, sector="bridge")

    if rh_decision.mode == "freeze_and_rebuild_closure" or ci < 0.76 or err > 5.8:
        mode = "safe"
        notes = "Nonlocal/Euler defect too high: use conservative execution."
        dt_override = 0.018
        zeta_scale = 0.30
    elif rh_decision.mode == "slow_execution_local_correction" or ci < 0.88 or err > 5.2:
        mode = "standard"
        notes = "Stable but not deep-merge safe."
        dt_override = 0.0205
        zeta_scale = 0.35
    else:
        mode = "deep"
        notes = "Strong coherence and closure: allow deeper diagnostic/integration passes."
        dt_override = 0.022
        zeta_scale = 0.38

    zeta_phase = float(final.get("zeta_effective_phase", 0.0) or 0.0)
    nonlocal_gate = coherent_fraction >= 0.15 and eba_defect <= 0.35
    euler_memory_lock = closure_score >= 0.45 and phase_gap <= 0.35
    writeback_gate = bool(mode != "safe" and nonlocal_gate and euler_memory_lock and rh_decision.severity != "high")
    target_phase_shift = -zeta_phase + 0.25 * target_phase

    return {
        "mode": mode,
        "phase_lock_enable": True,
        "target_phase_shift": target_phase_shift,
        "target_phase_memory": target_phase,
        "dt_override": dt_override,
        "zeta_coupling_scale": zeta_scale,
        "mu_phi": 0.18 if mode != "safe" else 0.16,
        "epsilon_hom": 0.22 if mode != "safe" else 0.18,
        "nonlocal_gate": nonlocal_gate,
        "euler_memory_lock": euler_memory_lock,
        "writeback_gate": writeback_gate,
        "rh_mode": rh_decision.mode,
        "rh_severity": rh_decision.severity,
        "rh_effective": rh_decision.effective_rh,
        "rh_drivers": rh_decision.drivers,
        "notes": notes,
    }


def build_state_manifest(final: dict) -> dict:
    rh_eff, _drivers = effective_rh(final)
    return {
        "coherence_index": coherence_index_from_snapshot(final),
        "topological_charge_global": topological_charge_global(final),
        "phase_lock_error": phase_lock_error(final),
        "beat_frequency_target_hz": 7.83,
        "spectral_radius_A": float(final.get("spectral_radius_A", 0.0)),
        "fiedler_L": float(final.get("fiedler_L", 0.0)),
        "zeta_enabled": bool(final.get("zeta_enabled", False)),
        "nonlocal_phi_ab_mean": _obs(final, "nonlocal_phi_ab_mean", "phi_ab_mean"),
        "nonlocal_phi_berry_mean": _obs(final, "nonlocal_phi_berry_mean", "phi_berry_mean"),
        "nonlocal_eba_defect_mean": _obs(final, "nonlocal_eba_defect_mean", "eba_defect_mean"),
        "nonlocal_coherent_fraction": _obs(final, "nonlocal_coherent_fraction", "coherent_fraction"),
        "euler_bridge_closure_score": _obs(final, "euler_bridge_closure_score", "bridge_closure_score", "closure_score"),
        "euler_bridge_target_phase": _obs(final, "euler_bridge_target_phase", "bridge_target_phase", "target_phase"),
        "effective_rh": rh_eff,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def build_health_manifest(final: dict) -> dict:
    ci = coherence_index_from_snapshot(final)
    err = phase_lock_error(final)
    rh_eff, drivers = effective_rh(final)
    closure_score = max(0.0, min(1.0, _obs(final, "euler_bridge_closure_score", "bridge_closure_score", "closure_score")))
    health = max(0.0, min(1.0, (0.55 * ci + 0.20 * closure_score + 0.25 * (1.0 - rh_eff)) / (1.0 + 0.08 * err)))
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
        "effective_rh": rh_eff,
        "rh_drivers": drivers,
        "recommended_action": action,
    }
