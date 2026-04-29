"""Orbital-style bridge into the holonomic M0–M8 memory sector.

The monolith TMP/TSM/WPM layer already captures durable records, but the
runtime still needs a native orbital trace written into the phase memory sector.
This module converts orbital/runtime state into a conservative event for the
HolonomicMemoryOrchestrator so memory is stored as a trajectory residue, not
just flat metadata.
"""

from __future__ import annotations

from dataclasses import asdict
import math
from typing import Any, Dict, Optional

from ciel_omega.ciel.orbital_memory_loop import OrbitalLoopResult
from ciel_omega.memory import HolonomicMemoryOrchestrator
from ciel_omega.ciel.orbital_memory_persistence import PersistentOrbitalSectorMemory


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(value)))


def _wrap_phase(value: float) -> float:
    return float(value % (2.0 * math.pi))


def derive_orbital_memory_phase(orbital: OrbitalLoopResult) -> float:
    final = orbital.final or {}
    control = orbital.control or {}
    base_phase = float(final.get("zeta_effective_phase", 0.0) or 0.0)
    shift = float(control.get("target_phase_shift", 0.0) or 0.0)
    return _wrap_phase(base_phase + shift)


def build_orbital_memory_event(
    *,
    text: str,
    context: str,
    mood: float,
    ethical_score: float,
    soul_invariant: float,
    orbital: OrbitalLoopResult,
    runtime_policy: Dict[str, Any],
    monolith_memory: Optional[Dict[str, str]] = None,
    memory_governor: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    final = orbital.final or {}
    control = orbital.control or {}
    state = orbital.state_manifest or {}
    health = orbital.health_manifest or {}
    diagnostics = orbital.diagnostics or {}

    coherence = _clamp(state.get("coherence_index", 0.0))
    system_health = _clamp(health.get("system_health", 0.0))
    r_h = _clamp(1.0 - float(final.get("R_H", 1.0)), 0.0, 1.0)
    closure_penalty = max(0.0, float(final.get("closure_penalty", 0.0) or 0.0))
    closure_stress = closure_penalty / (1.0 + closure_penalty)
    radial_spread = _clamp(float(final.get("radial_spread", 0.0) or 0.0), 0.0, 1.0)
    euler_leak = abs(float(final.get("euler_leak_angle", 0.0) or 0.0)) / math.pi
    lambda_glob = abs(float(final.get("Lambda_glob", 0.0) or 0.0))
    text_load = _clamp(len(text) / 256.0)

    salience = _clamp(0.20 + 0.28 * closure_stress + 0.14 * lambda_glob + 0.18 * coherence + 0.10 * text_load + 0.10 * abs(mood - 0.5) * 2.0)
    confidence = _clamp(0.20 + 0.38 * system_health + 0.16 * coherence + 0.14 * ethical_score + 0.12 * soul_invariant)
    novelty = _clamp(0.10 + 0.30 * radial_spread + 0.20 * euler_leak + 0.18 * (1.0 - system_health) + 0.10 * text_load)
    identity_impact = _clamp(0.18 + 0.30 * soul_invariant + 0.18 * coherence + 0.14 * ethical_score + 0.10 * (1.0 - closure_stress))
    phase = derive_orbital_memory_phase(orbital)

    loop_bias = "identity_stabilization" if control.get("mode") == "safe" else ("deep" if control.get("mode") == "deep" else "short")
    result_success = bool(runtime_policy.get("durable_write_allowed", False))

    orbital_context = {
        "pipeline": "relation->orbital->orchestration->reduction->memory",
        "runtime_context": context,
        "control_mode": control.get("mode", "safe"),
        "rh_mode": orbital.rh_policy.get("mode", "freeze_and_rebuild_closure"),
        "rh_severity": orbital.rh_policy.get("severity", "high"),
        "loop_bias": loop_bias,
        "dominant_residual_sector": diagnostics.get("dominant_residual_sector"),
        "dominant_vorticity_sector": diagnostics.get("dominant_vorticity_sector"),
        "dominant_mass_sector": diagnostics.get("dominant_mass_sector"),
        "R_H": float(final.get("R_H", 1.0) or 1.0),
        "closure_penalty": closure_penalty,
        "Lambda_glob": float(final.get("Lambda_glob", 0.0) or 0.0),
        "zeta_effective_tau": float(final.get("zeta_effective_tau", 0.0) or 0.0),
        "zeta_effective_phase": float(final.get("zeta_effective_phase", 0.0) or 0.0),
        "euler_leak_angle": float(final.get("euler_leak_angle", 0.0) or 0.0),
        "orbital_status": orbital.status,
    }
    if monolith_memory is not None:
        orbital_context["durable_memory_ref"] = monolith_memory.get("memorise_id")
    if memory_governor is not None:
        orbital_context["consolidation_mode"] = memory_governor.get("consolidation_mode")
        orbital_context["consolidation_focus"] = memory_governor.get("consolidation_focus")

    event = {
        "content": text,
        "modality": "orbital_text",
        "phase": phase,
        "salience": salience,
        "confidence": confidence,
        "novelty": novelty,
        "identity_impact": identity_impact,
        "context": orbital_context,
        "goal": "stabilize_orbital_trace",
        "action": "record_orbital_memory_residue",
        "objective": f"{control.get('mode', 'safe')}_closure_guided_memory",
        "polarity": "truth_aligned",
        "result": {
            "success": result_success,
            "durable_write_allowed": result_success,
            "require_trusted_source_for_promotion": bool(runtime_policy.get("require_trusted_source_for_promotion", False)),
            "response_strategy": runtime_policy.get("response_strategy", "stabilize_then_answer"),
        },
        "memory_governor": memory_governor or {},
        "orbital_trace": {
            "phase": phase,
            "coherence_index": coherence,
            "system_health": system_health,
            "control_mode": control.get("mode", "safe"),
            "loop_bias": loop_bias,
        },
    }
    return event


def record_orbital_sector_memory(
    *,
    sector_memory: HolonomicMemoryOrchestrator | PersistentOrbitalSectorMemory,
    text: str,
    context: str,
    mood: float,
    ethical_score: float,
    soul_invariant: float,
    orbital: OrbitalLoopResult,
    runtime_policy: Dict[str, Any],
    monolith_memory: Optional[Dict[str, str]] = None,
    memory_governor: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = build_orbital_memory_event(
        text=text,
        context=context,
        mood=mood,
        ethical_score=ethical_score,
        soul_invariant=soul_invariant,
        orbital=orbital,
        runtime_policy=runtime_policy,
        monolith_memory=monolith_memory,
        memory_governor=memory_governor,
    )
    if hasattr(sector_memory, "record"):
        recorded = sector_memory.record(event)
        cycle = recorded.get("cycle")
        snapshot = recorded.get("snapshot")
        retrieval = recorded.get("retrieval")
        store_path = recorded.get("store_path")
        restored_events = int(recorded.get("restored_events", 0) or 0)
    else:
        cycle = sector_memory.process_input(event["content"], metadata={k: v for k, v in event.items() if k != "content"})
        snapshot = sector_memory.snapshot()
        retrieval = sector_memory.retrieve(text, top_k=3)
        store_path = None
        restored_events = 0
    return {
        "event": event,
        "cycle": asdict(cycle) if hasattr(cycle, "__dataclass_fields__") else cycle,
        "snapshot": asdict(snapshot) if hasattr(snapshot, "__dataclass_fields__") else snapshot,
        "retrieval": retrieval,
        "store_path": store_path,
        "restored_events": restored_events,
    }


__all__ = [
    "derive_orbital_memory_phase",
    "build_orbital_memory_event",
    "record_orbital_sector_memory",
]
