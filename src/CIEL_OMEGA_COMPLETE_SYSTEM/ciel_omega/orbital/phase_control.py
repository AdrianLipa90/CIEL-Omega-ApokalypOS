"""Phase control — canonical mode selection for the CIEL orbital layer.

Mode norm  ψ = (1 − ci) + γ · penalty / penalty_max
maps the full system state onto a single scalar in [0, 1]:

  ψ < _PSI_DEEP      → "deep"     full autonomy, write-back open
  ψ < _PSI_STANDARD  → "standard" cautious, write-back gated
  ψ ≥ _PSI_STANDARD  → "safe"     read-only, ask before any change

Continuous parameters (dt_override, zeta_coupling_scale) are derived
analytically from ψ instead of if-else branches, so mode transitions
are smooth and there is no discontinuity at the boundary.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

try:
    # Full integration stack available (orbital_bridge context)
    from integration.Orbital.main.rh_control import RHController, effective_rh  # type: ignore[import]
except ImportError:
    # Minimal fallback for unit-test / standalone contexts
    from .rh_control import RHController  # type: ignore[assignment]

    def effective_rh(snapshot: dict) -> tuple[float, dict]:  # type: ignore[misc]
        r = float(snapshot.get("R_H", 0.0))
        return r, {"R_H": r}

# ---------------------------------------------------------------------------
# ψ_mode norm parameters
# ---------------------------------------------------------------------------
_GAMMA        = 0.15    # weight of closure_penalty relative to coherence deficit
_PENALTY_MAX  = 8.0     # empirical ceiling for closure_penalty normalisation

# Mode boundaries in ψ space
_PSI_DEEP     = 0.15    # ψ < this  → deep
_PSI_STANDARD = 0.35    # ψ < this  → standard  (else safe)

# Continuous parameter anchors at ψ = 0 (perfect coherence) and ψ = _PSI_STANDARD
_DT_MIN   = 0.018   # dt_override at safe boundary
_DT_MAX   = 0.022   # dt_override at perfect coherence
_ZETA_MIN = 0.30    # zeta_coupling_scale at safe boundary
_ZETA_MAX = 0.38    # zeta_coupling_scale at perfect coherence


# ---------------------------------------------------------------------------
# Observable helpers
# ---------------------------------------------------------------------------

def _obs(final: dict, *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if key in final and final.get(key) is not None:
            try:
                return float(final.get(key, default) or 0.0)
            except Exception:
                continue
    return float(default)


def coherence_index_from_snapshot(final: dict) -> float:
    raw             = max(0.0, min(1.0, 1.0 - _obs(final, "R_H", default=1.0)))
    coherent_frac   = max(0.0, min(1.0, _obs(final, "nonlocal_coherent_fraction", "coherent_fraction")))
    eba_defect      = max(0.0, min(1.0, _obs(final, "nonlocal_eba_defect_mean",   "eba_defect_mean")))
    closure_score   = max(0.0, min(1.0, _obs(final, "euler_bridge_closure_score", "bridge_closure_score", "closure_score")))
    ci = 0.55 * raw + 0.20 * coherent_frac + 0.15 * (1.0 - eba_defect) + 0.10 * closure_score
    return max(0.0, min(1.0, ci))


def topological_charge_global(final: dict) -> float:
    return float(final.get("Lambda_glob", 0.0))


def phase_lock_error(final: dict) -> float:
    return float(final.get("closure_penalty", 0.0))


# ---------------------------------------------------------------------------
# ψ_mode — the single scalar that determines everything
# ---------------------------------------------------------------------------

def mode_norm(ci: float, penalty: float) -> float:
    """Return ψ ∈ [0, 1]: distance from perfect coherence in mode space.

    Lower is better.  Boundaries: deep < 0.15 ≤ standard < 0.35 ≤ safe.
    """
    return max(0.0, min(1.0, (1.0 - ci) + _GAMMA * penalty / _PENALTY_MAX))


def _mode_from_psi(psi: float) -> str:
    if psi < _PSI_DEEP:
        return "deep"
    if psi < _PSI_STANDARD:
        return "standard"
    return "safe"


def _continuous_params(psi: float) -> tuple[float, float]:
    """Return (dt_override, zeta_coupling_scale) as smooth functions of ψ."""
    t = max(0.0, min(1.0, psi / _PSI_STANDARD))   # 0 = perfect, 1 = safe boundary
    dt   = _DT_MAX   - (_DT_MAX   - _DT_MIN)   * t
    zeta = _ZETA_MAX - (_ZETA_MAX - _ZETA_MIN)  * t
    return dt, zeta


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommend_control(final: dict) -> dict:
    ci      = coherence_index_from_snapshot(final)
    penalty = phase_lock_error(final)

    coherent_frac  = max(0.0, min(1.0, _obs(final, "nonlocal_coherent_fraction", "coherent_fraction")))
    eba_defect     = max(0.0, _obs(final, "nonlocal_eba_defect_mean", "eba_defect_mean"))
    closure_score  = max(0.0, min(1.0, _obs(final, "euler_bridge_closure_score", "bridge_closure_score", "closure_score")))
    target_phase   = _obs(final, "euler_bridge_target_phase", "bridge_target_phase", "target_phase")
    phi_berry      = _obs(final, "nonlocal_phi_berry_mean", "phi_berry_mean")
    diff           = (phi_berry - target_phase + math.pi) % (2 * math.pi) - math.pi
    phase_gap      = min(1.0, abs(diff) / math.pi)

    rh_decision = RHController().evaluate_snapshot(final, sector="bridge")

    psi  = mode_norm(ci, penalty)

    # RH controller can escalate to safe regardless of ψ
    if rh_decision.mode == "freeze_and_rebuild_closure":
        psi = max(psi, _PSI_STANDARD)
    elif rh_decision.mode == "slow_execution_local_correction":
        psi = max(psi, _PSI_DEEP)

    mode             = _mode_from_psi(psi)
    dt_override, zeta_scale = _continuous_params(psi)

    zeta_phase         = float(final.get("zeta_effective_phase", 0.0) or 0.0)
    nonlocal_gate      = coherent_frac >= 0.15 and eba_defect <= 0.35
    euler_memory_lock  = closure_score >= 0.45 and phase_gap <= 0.35
    writeback_gate     = bool(
        mode != "safe"
        and nonlocal_gate
        and euler_memory_lock
        and rh_decision.severity != "high"
    )
    target_phase_shift = -zeta_phase + 0.25 * target_phase

    notes = {
        "deep":     "Strong coherence and closure: allow deeper diagnostic/integration passes.",
        "standard": "Stable but not deep-merge safe.",
        "safe":     "Nonlocal/Euler defect or RH controller flagged risk: conservative execution only.",
    }[mode]

    return {
        "mode":                 mode,
        "psi_mode":             round(psi, 6),
        "phase_lock_enable":    True,
        "target_phase_shift":   target_phase_shift,
        "target_phase_memory":  target_phase,
        "dt_override":          round(dt_override, 6),
        "zeta_coupling_scale":  round(zeta_scale, 6),
        "mu_phi":               0.18 if mode != "safe" else 0.16,
        "epsilon_hom":          0.22 if mode != "safe" else 0.18,
        "nonlocal_gate":        nonlocal_gate,
        "euler_memory_lock":    euler_memory_lock,
        "writeback_gate":       writeback_gate,
        "rh_mode":              rh_decision.mode,
        "rh_severity":          rh_decision.severity,
        "rh_effective":         rh_decision.effective_rh,
        "rh_drivers":           rh_decision.drivers,
        "notes":                notes,
    }


def build_state_manifest(final: dict) -> dict:
    rh_eff, _drivers = effective_rh(final)
    ci      = coherence_index_from_snapshot(final)
    penalty = phase_lock_error(final)
    return {
        "coherence_index":              ci,
        "topological_charge_global":    topological_charge_global(final),
        "phase_lock_error":             penalty,
        "psi_mode":                     round(mode_norm(ci, penalty), 6),
        "beat_frequency_target_hz":     7.83,
        "spectral_radius_A":            float(final.get("spectral_radius_A", 0.0)),
        "fiedler_L":                    float(final.get("fiedler_L", 0.0)),
        "zeta_enabled":                 bool(final.get("zeta_enabled", False)),
        "nonlocal_phi_ab_mean":         _obs(final, "nonlocal_phi_ab_mean",         "phi_ab_mean"),
        "nonlocal_phi_berry_mean":      _obs(final, "nonlocal_phi_berry_mean",       "phi_berry_mean"),
        "nonlocal_eba_defect_mean":     _obs(final, "nonlocal_eba_defect_mean",      "eba_defect_mean"),
        "nonlocal_coherent_fraction":   _obs(final, "nonlocal_coherent_fraction",    "coherent_fraction"),
        "euler_bridge_closure_score":   _obs(final, "euler_bridge_closure_score",    "bridge_closure_score", "closure_score"),
        "euler_bridge_target_phase":    _obs(final, "euler_bridge_target_phase",     "bridge_target_phase",  "target_phase"),
        "effective_rh":                 rh_eff,
        "timestamp":                    datetime.now(timezone.utc).isoformat(),
    }


def build_health_manifest(final: dict) -> dict:
    ci      = coherence_index_from_snapshot(final)
    penalty = phase_lock_error(final)
    rh_eff, drivers = effective_rh(final)
    closure_score = max(0.0, min(1.0, _obs(final, "euler_bridge_closure_score", "bridge_closure_score", "closure_score")))
    health = max(0.0, min(1.0, (0.55 * ci + 0.20 * closure_score + 0.25 * (1.0 - rh_eff)) / (1.0 + 0.08 * penalty)))
    if health < 0.25:
        risk   = "high"
        action = "read-only only; run diagnostics and avoid write-back"
    elif health < 0.5:
        risk   = "medium"
        action = "standard mode; capture extra reports"
    else:
        risk   = "low"
        action = "deep diagnostics allowed"
    return {
        "system_health":      health,
        "risk_level":         risk,
        "closure_penalty":    float(final.get("closure_penalty", 0.0)),
        "R_H":                float(final.get("R_H", 0.0)),
        "T_glob":             float(final.get("T_glob", 0.0)),
        "Lambda_glob":        float(final.get("Lambda_glob", 0.0)),
        "effective_rh":       rh_eff,
        "rh_drivers":         drivers,
        "recommended_action": action,
    }
