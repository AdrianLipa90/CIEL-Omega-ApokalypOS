from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


def _get(src: Mapping[str, Any] | None, key: str, default: Any = None) -> Any:
    if not isinstance(src, Mapping):
        return default
    return src.get(key, default)


@dataclass(frozen=True)
class PhaseSnapshot:
    phase_snapshot_id: str
    event_id: str | None
    cycle_index: int
    identity_phase: float
    coherence_index: float
    closure_penalty: float
    system_health: float
    ethical_score: float
    identity_drift: float
    phase_velocity: float
    euler_residual: float
    attractor_dist: float
    memory_projection_confidence: float
    memory_projection_residual: float
    lingo_phase_target: float
    lingo_phase_shift: float
    lingo_phase_confidence: float
    lingo_tau_gradient_mean: float
    lingo_imaginal_drive: float
    ts: str


@dataclass(frozen=True)
class QualisensingSnapshot:
    qualisensing_id: str
    event_id: str | None
    phase_snapshot_id: str
    dominant_emotion: str
    sub_affect: str
    sub_impulse: str
    sub_latency: float
    mnemonic_pressure: float
    symbolic_pull: float
    recurrence_pressure: float
    imaginal_drive: float
    tau_gradient_mean: float
    closure_tension: float
    coherence_tension: float
    field_confidence: float
    ts: str


def build_phase_snapshot(state: Mapping[str, Any]) -> PhaseSnapshot:
    lingo_phase = _get(state, "lingo_phase_projection", {}) if isinstance(_get(state, "lingo_phase_projection", {}), Mapping) else {}
    return PhaseSnapshot(
        phase_snapshot_id=f"phase:{int(_get(state, 'cycle_index', 0) or 0)}:{int(float(_get(state, 'identity_phase', 0.0) or 0.0) * 1_000_000)}",
        event_id=str(_get(state, "event_id", "") or "") or None,
        cycle_index=int(_get(state, "cycle_index", 0) or 0),
        identity_phase=float(_get(state, "identity_phase", 0.0) or 0.0),
        coherence_index=float(_get(state, "coherence_index", 0.0) or 0.0),
        closure_penalty=float(_get(state, "closure_penalty", 0.0) or 0.0),
        system_health=float(_get(state, "system_health", 0.0) or 0.0),
        ethical_score=float(_get(state, "ethical_score", 0.0) or 0.0),
        identity_drift=float(_get(state, "identity_drift", 0.0) or 0.0),
        phase_velocity=float(_get(state, "phase_velocity", 0.0) or 0.0),
        euler_residual=float(_get(state, "euler_residual", 0.0) or 0.0),
        attractor_dist=float(_get(state, "attractor_dist", 0.0) or 0.0),
        memory_projection_confidence=float(_get(state, "memory_projection_confidence", 0.0) or 0.0),
        memory_projection_residual=float(_get(state, "memory_projection_residual", 1.0) or 1.0),
        lingo_phase_target=float(_get(lingo_phase, "target_phase", 0.0) or 0.0),
        lingo_phase_shift=float(_get(lingo_phase, "target_phase_shift", 0.0) or 0.0),
        lingo_phase_confidence=float(_get(lingo_phase, "phase_confidence", 0.0) or 0.0),
        lingo_tau_gradient_mean=float(_get(state, "lingo_tau_gradient_mean", 0.0) or 0.0),
        lingo_imaginal_drive=float(_get(state, "lingo_imaginal_drive", 0.0) or 0.0),
        ts=str(_get(state, "ts", "") or ""),
    )


def build_qualisensing_snapshot(state: Mapping[str, Any], *, phase_snapshot_id: str) -> QualisensingSnapshot:
    return QualisensingSnapshot(
        qualisensing_id=f"quali:{int(_get(state, 'cycle_index', 0) or 0)}:{int(float(_get(state, 'coherence_index', 0.0) or 0.0) * 1_000_000)}",
        event_id=str(_get(state, "event_id", "") or "") or None,
        phase_snapshot_id=phase_snapshot_id,
        dominant_emotion=str(_get(state, "dominant_emotion", "") or ""),
        sub_affect=str(_get(state, "sub_affect", _get(state, "subconscious_note", "") or "") or ""),
        sub_impulse=str(_get(state, "sub_impulse", "") or ""),
        sub_latency=float(_get(state, "sub_latency", 0.0) or 0.0),
        mnemonic_pressure=float(_get(state, "jokeheal_mnemonic_pressure", _get(state, "mnemonic_pressure", 0.0)) or 0.0),
        symbolic_pull=float(_get(state, "jokeheal_symbolic_pull", _get(state, "symbolic_pull", 0.0)) or 0.0),
        recurrence_pressure=float(_get(state, "jokeheal_recurrence_pressure", _get(state, "recurrence_pressure", 0.0)) or 0.0),
        imaginal_drive=float(_get(state, "lingo_imaginal_drive", _get(state, "imaginal_drive", 0.0)) or 0.0),
        tau_gradient_mean=float(_get(state, "lingo_tau_gradient_mean", _get(state, "tau_gradient_mean", 0.0)) or 0.0),
        closure_tension=float(_get(state, "closure_penalty", 0.0) or 0.0),
        coherence_tension=max(0.0, 1.0 - float(_get(state, "coherence_index", 0.0) or 0.0)),
        field_confidence=float(_get(state, "memory_projection_confidence", 0.0) or 0.0),
        ts=str(_get(state, "ts", "") or ""),
    )


def snapshot_to_dict(snapshot: PhaseSnapshot | QualisensingSnapshot) -> dict[str, Any]:
    return asdict(snapshot)
