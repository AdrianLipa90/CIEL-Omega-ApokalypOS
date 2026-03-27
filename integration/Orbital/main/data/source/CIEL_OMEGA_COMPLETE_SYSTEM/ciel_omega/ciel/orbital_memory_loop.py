"""Bridge orbital diagnostics into runtime and durable memory.

This module turns the previously detached orbital subsystem into a runtime loop:

input -> orbital snapshot -> control recommendation -> memory capture/promotion

The bridge is intentionally conservative:
- orbital failures never crash the engine; they are surfaced in-band,
- memory metadata carries topological health and policy state,
- wave attrs store the orbital/control snapshot alongside the durable record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ciel_omega.orbital.global_pass import run_global_pass
from ciel_omega.orbital.phase_control import (
    build_health_manifest,
    build_state_manifest,
    recommend_control,
)
from ciel_omega.orbital.rh_control import RHController


@dataclass(frozen=True)
class RuntimeOrbitalSignals:
    text_length: int = 0
    context: str = "runtime"
    mood: float = 0.5
    ethical_score: float = 0.5
    soul_invariant: float = 0.5
    simulation_coherence: float = 0.5
    intention_norm: float = 0.0


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def derive_runtime_orbital_params(signals: RuntimeOrbitalSignals) -> Dict[str, float]:
    stability = _clamp(
        0.50 * signals.soul_invariant + 0.25 * signals.simulation_coherence + 0.15 * signals.ethical_score + 0.10 * (1.0 - abs(signals.mood - 0.5) * 2.0),
        0.0,
        1.0,
    )
    load = _clamp(signals.text_length / 240.0, 0.0, 1.0)
    intent = _clamp(signals.intention_norm / 6.0, 0.0, 1.0)
    context_l = signals.context.lower()
    deliberative = any(tok in context_l for tok in ("research", "audit", "analysis", "orbital", "theory"))
    fast_lane = any(tok in context_l for tok in ("chat", "dialogue", "once", "quick"))

    dt = 0.0195 - 0.0075 * stability + 0.0020 * load - 0.0010 * intent
    mesh_boost = 0.74 + 0.16 * load + 0.12 * (1.0 - stability)
    mu_phi = 0.065 + 0.08 * load + 0.055 * (1.0 - stability) + 0.02 * intent
    zeta_scale = 0.28 + 0.07 * stability

    if deliberative:
        dt -= 0.0015
        mesh_boost -= 0.05
        mu_phi -= 0.015
    if fast_lane:
        dt += 0.0005
        mesh_boost += 0.02

    return {
        "dt": round(_clamp(dt, 0.010, 0.022), 6),
        "mesh_boost": round(_clamp(mesh_boost, 0.60, 0.92), 6),
        "mu_phi": round(_clamp(mu_phi, 0.05, 0.16), 6),
        "zeta_coupling_scale": round(_clamp(zeta_scale, 0.25, 0.36), 6),
    }


@dataclass(frozen=True)
class OrbitalLoopConfig:
    steps: int = 2
    context_prefix: str = "orbital-runtime"
    write_reports: bool = True
    pass_label: str = "runtime"
    params: Dict[str, float] = field(default_factory=dict)
    runtime_signals: Optional[RuntimeOrbitalSignals] = None


@dataclass
class OrbitalLoopResult:
    status: str
    final: Dict[str, Any]
    state_manifest: Dict[str, Any]
    health_manifest: Dict[str, Any]
    control: Dict[str, Any]
    rh_policy: Dict[str, Any]
    history_length: int
    params: Dict[str, float]
    diagnostics: Dict[str, Any]
    runtime_signals: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "final": self.final,
            "state_manifest": self.state_manifest,
            "health_manifest": self.health_manifest,
            "control": self.control,
            "rh_policy": self.rh_policy,
            "history_length": self.history_length,
            "params": self.params,
            "diagnostics": self.diagnostics,
            "runtime_signals": self.runtime_signals,
            "error": self.error,
        }


def run_orbital_loop(config: OrbitalLoopConfig | None = None) -> OrbitalLoopResult:
    cfg = config or OrbitalLoopConfig()
    runtime_signals = cfg.runtime_signals or RuntimeOrbitalSignals(context=cfg.pass_label or cfg.context_prefix)
    effective_params = dict(cfg.params)
    derived = derive_runtime_orbital_params(runtime_signals)
    for key, value in derived.items():
        effective_params.setdefault(key, value)
    try:
        payload = run_global_pass(
            steps=cfg.steps,
            params=effective_params,
            write_reports=cfg.write_reports,
            pass_label=cfg.pass_label,
        )
        final = payload.get("final", {})
        state_manifest = build_state_manifest(final)
        health_manifest = build_health_manifest(final)
        control = recommend_control(final)
        rh = RHController().evaluate(float(final.get("R_H", 1.0)), sector="runtime")
        control = dict(control)
        control["rh_mode"] = rh.mode
        control["rh_severity"] = rh.severity
        control["sector_overrides"] = rh.sector_overrides
        return OrbitalLoopResult(
            status="ok",
            final=final,
            state_manifest=state_manifest,
            health_manifest=health_manifest,
            control=control,
            rh_policy={
                "mode": rh.mode,
                "severity": rh.severity,
                "allowed_actions": rh.allowed_actions,
                "discouraged_actions": rh.discouraged_actions,
                "actions": rh.actions,
                "sector_overrides": rh.sector_overrides,
                "notes": rh.notes,
            },
            history_length=len(payload.get("history", [])),
            params=effective_params,
            diagnostics=payload.get("diagnostics", {}),
            runtime_signals=runtime_signals.__dict__.copy(),
        )
    except Exception as exc:  # pragma: no cover - exercised by runtime fallback only
        return OrbitalLoopResult(
            status="degraded",
            final={},
            state_manifest={},
            health_manifest={},
            control={
                "mode": "safe",
                "phase_lock_enable": False,
                "target_phase_shift": 0.0,
                "dt_override": None,
                "zeta_coupling_scale": None,
                "notes": "Orbital loop unavailable; runtime continues in degraded mode.",
            },
            rh_policy={
                "mode": "freeze_and_rebuild_closure",
                "severity": "high",
                "allowed_actions": ["resolve", "report", "stabilize", "link", "archive"],
                "discouraged_actions": ["merge", "broad_route", "speculative_refactor", "execution_burst"],
                "actions": ["Freeze merges.", "Prioritize diagnosis over execution."],
                "sector_overrides": {"runtime": ["Reduce execution tempo.", "Check memory synchronization before new runs."]},
                "notes": ["Orbital loop unavailable; runtime forced into degraded closure policy."],
            },
            history_length=0,
            params=effective_params,
            diagnostics={},
            runtime_signals=runtime_signals.__dict__.copy(),
            error=f"{type(exc).__name__}: {exc}",
        )


def _coherence_flags(final: Dict[str, Any], health: Dict[str, Any]) -> Dict[str, Any]:
    r_h = float(final.get("R_H", 1.0))
    closure = float(final.get("closure_penalty", 999.0))
    health_score = float(health.get("system_health", 0.0))
    return {
        "trusted_source": health_score >= 0.45,
        "novelty_hint": r_h <= 0.30,
        "contradiction_flag": closure >= 6.0,
        "ethics_warning": health.get("risk_level") == "high",
        "orbital_r_h": r_h,
        "orbital_closure_penalty": closure,
        "orbital_health": health_score,
    }


def build_memory_meta(
    *,
    text: str,
    context: str,
    mood: float,
    ethical_score: float,
    soul_invariant: float,
    orbital: OrbitalLoopResult,
    runtime_policy: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    policy = runtime_policy or build_runtime_policy(orbital)
    meta = {
        "context": context,
        "input_length": len(text),
        "mood": float(mood),
        "ethical_score": float(ethical_score),
        "soul_invariant": float(soul_invariant),
        "orbital_status": orbital.status,
        "orbital_control_mode": orbital.control.get("mode", "safe"),
        "orbital_target_phase_shift": orbital.control.get("target_phase_shift", 0.0),
        "orbital_rh_mode": orbital.rh_policy.get("mode", "freeze_and_rebuild_closure"),
        "orbital_rh_severity": orbital.rh_policy.get("severity", "high"),
        "orbital_dominant_residual_sector": orbital.diagnostics.get("dominant_residual_sector"),
        "tmp_pass_threshold": float(policy.get("tmp_pass_threshold", 0.70)),
        "tmp_hold_threshold": float(policy.get("tmp_hold_threshold", 0.40)),
        "durable_write_allowed": bool(policy.get("durable_write_allowed", False)),
        "require_trusted_source_for_promotion": bool(policy.get("require_trusted_source_for_promotion", False)),
    }
    meta.update(_coherence_flags(orbital.final, orbital.health_manifest))
    if orbital.error:
        meta["orbital_error"] = orbital.error
    return meta


def build_wave_attrs(
    *,
    text: str,
    context: str,
    orbital: OrbitalLoopResult,
    ethical_score: float,
    soul_invariant: float,
) -> Dict[str, Any]:
    final = orbital.final
    return {
        "context": context,
        "input_preview": text[:160],
        "orbital_status": orbital.status,
        "orbital_history_length": orbital.history_length,
        "control_mode": orbital.control.get("mode", "safe"),
        "rh_mode": orbital.rh_policy.get("mode", "freeze_and_rebuild_closure"),
        "coherence_index": orbital.state_manifest.get("coherence_index", 0.0),
        "system_health": orbital.health_manifest.get("system_health", 0.0),
        "dominant_residual_sector": orbital.diagnostics.get("dominant_residual_sector"),
        "dominant_vorticity_sector": orbital.diagnostics.get("dominant_vorticity_sector"),
        "R_H": final.get("R_H", 1.0),
        "closure_penalty": final.get("closure_penalty", 999.0),
        "Lambda_glob": final.get("Lambda_glob", 0.0),
        "T_glob": final.get("T_glob", 0.0),
        "ethical_score": float(ethical_score),
        "soul_invariant": float(soul_invariant),
    }


def build_runtime_policy(orbital: OrbitalLoopResult) -> Dict[str, Any]:
    control_mode = orbital.control.get("mode", "safe")
    rh_severity = orbital.rh_policy.get("severity", "high")

    if control_mode == "deep":
        response_strategy = "allow_richer_generation"
        memory_bias = "promote_if_bifurcated"
        tmp_pass_threshold = 0.66
        tmp_hold_threshold = 0.38
        durable_write_allowed = True
        require_trusted_source = False
    elif control_mode == "standard":
        response_strategy = "balanced_generation"
        memory_bias = "capture_and_gate"
        tmp_pass_threshold = 0.70
        tmp_hold_threshold = 0.42
        durable_write_allowed = True
        require_trusted_source = False
    else:
        response_strategy = "conservative_generation"
        memory_bias = "capture_with_caution"
        tmp_pass_threshold = 0.78
        tmp_hold_threshold = 0.48
        durable_write_allowed = False
        require_trusted_source = True

    if rh_severity == "medium":
        tmp_pass_threshold = max(tmp_pass_threshold, 0.74)
        tmp_hold_threshold = max(tmp_hold_threshold, 0.45)
        require_trusted_source = True
    elif rh_severity == "high":
        tmp_pass_threshold = max(tmp_pass_threshold, 0.82)
        tmp_hold_threshold = max(tmp_hold_threshold, 0.55)
        durable_write_allowed = False
        require_trusted_source = True

    return {
        "control_mode": control_mode,
        "response_strategy": response_strategy,
        "memory_bias": memory_bias,
        "rh_mode": orbital.rh_policy.get("mode", "freeze_and_rebuild_closure"),
        "rh_severity": rh_severity,
        "tmp_pass_threshold": tmp_pass_threshold,
        "tmp_hold_threshold": tmp_hold_threshold,
        "durable_write_allowed": durable_write_allowed,
        "require_trusted_source_for_promotion": require_trusted_source,
        "notes": orbital.control.get("notes", ""),
    }


__all__ = [
    "OrbitalLoopConfig",
    "OrbitalLoopResult",
    "RuntimeOrbitalSignals",
    "derive_runtime_orbital_params",
    "build_memory_meta",
    "build_runtime_policy",
    "build_wave_attrs",
    "run_orbital_loop",
]
