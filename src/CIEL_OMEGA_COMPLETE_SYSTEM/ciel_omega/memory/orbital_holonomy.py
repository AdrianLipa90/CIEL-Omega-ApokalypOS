from __future__ import annotations

import math
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List

from .base import CHANNEL_PARAMS
from .holonomy import HolonomyCalculator, create_loop_from_trajectory

CHANNEL_INDEX = {
    "perceptual": 0,
    "working": 1,
    "episodic": 2,
    "semantic": 3,
    "procedural": 4,
    "affective": 5,
    "identity": 6,
    "braid": 7,
}

RETRIEVAL_LOOPS = {
    "perceptual": [0, 6, 7, 6, 0],
    "working": [1, 6, 7, 6, 1],
    "episodic": [2, 6, 7, 6, 2],
    "semantic": [3, 6, 7, 6, 3],
    "procedural": [4, 6, 7, 6, 4],
    "affective": [5, 6, 7, 6, 5],
}

CONSOLIDATION_LOOPS = {
    "semantic": [2, 3, 6, 7, 6, 3, 2],
    "procedural": [2, 4, 6, 7, 6, 4, 2],
    "affective": [2, 5, 6, 7, 6, 5, 2],
}


def wrap_phase(value: float) -> float:
    return float(value % (2.0 * math.pi))


def phase_distance(a: float, b: float) -> float:
    delta = abs(float(a) - float(b)) % (2.0 * math.pi)
    return float(min(delta, 2.0 * math.pi - delta))


def current_orbital_phase(orbital: Dict[str, Any]) -> float:
    final = orbital.get("final") if isinstance(orbital, dict) and isinstance(orbital.get("final"), dict) else {}
    control = orbital.get("control") if isinstance(orbital, dict) and isinstance(orbital.get("control"), dict) else {}
    base = float(final.get("zeta_effective_phase", 0.0) or 0.0)
    shift = float(control.get("target_phase_shift", 0.0) or 0.0)
    return wrap_phase(base + shift)


def _coerce_snapshot(snapshot: Any) -> Dict[str, Any]:
    if is_dataclass(snapshot):
        return asdict(snapshot)
    if isinstance(snapshot, dict):
        return dict(snapshot)
    if hasattr(snapshot, "__dict__"):
        return dict(vars(snapshot))
    return {}


def sector_snapshot(obj: Any) -> Dict[str, Any]:
    snap = getattr(obj, "snapshot", None)
    if callable(snap):
        try:
            return _coerce_snapshot(snap())
        except Exception:
            return {}
    return {}


def state_phases(obj: Any) -> List[float]:
    direct_state = getattr(obj, "state", None)
    if direct_state is not None:
        phases = getattr(direct_state, "phases", None)
        if phases is not None:
            try:
                return [float(x) for x in phases]
            except Exception:
                pass
    orchestrator = getattr(obj, "orchestrator", None)
    if orchestrator is not None:
        state = getattr(orchestrator, "state", None)
        phases = getattr(state, "phases", None)
        if phases is not None:
            try:
                return [float(x) for x in phases]
            except Exception:
                pass
    return [0.0] * 8


def _loop_sequence(channel: str, *, kind: str) -> List[int]:
    if kind == "consolidation":
        return CONSOLIDATION_LOOPS.get(channel, [2, 6, 7, 6, 2])
    return RETRIEVAL_LOOPS.get(channel, [2, 6, 7, 6, 2])


def _trajectory_for(channel: str, *, kind: str, entry_phase: float, phases: List[float], identity_phase: float, braid_phase: float) -> List[float]:
    idx = CHANNEL_INDEX.get(channel, 2)
    episodic_phase = float(phases[2] if len(phases) > 2 else entry_phase)
    channel_phase = float(phases[idx] if len(phases) > idx else entry_phase)
    if kind == "consolidation":
        return [episodic_phase, channel_phase, identity_phase, braid_phase, identity_phase, entry_phase, episodic_phase]
    return [channel_phase, identity_phase, braid_phase, identity_phase, entry_phase]


def compute_holonomic_profile(channel: str, *, entry_phase: float, holder: Any, orbital: Dict[str, Any], kind: str) -> Dict[str, Any]:
    idx = CHANNEL_INDEX.get(channel)
    orbital_phase = current_orbital_phase(orbital)
    if idx is None:
        return {
            "entry_phase": float(entry_phase),
            "current_phase": 0.0,
            "orbital_phase": float(orbital_phase),
            "identity_phase": 0.0,
            "phase_alignment": 0.0,
            "identity_attractor_score": 0.0,
            "closure_quality": 0.0,
            "eba_quality": 0.0,
            "holonomy_quality": 0.0,
            "holonomy_defect": math.pi,
            "loop_coherent": False,
            "loop_type": f"{kind}_{channel}",
        }

    phases = state_phases(holder)
    snapshot = sector_snapshot(holder)
    identity_phase = float(snapshot.get("identity_phase", phases[6] if len(phases) > 6 else 0.0) or 0.0)
    braid_phase = float(phases[7] if len(phases) > 7 else identity_phase)
    current_phase = float(phases[idx] if len(phases) > idx else entry_phase)
    entry_phase = wrap_phase(entry_phase)

    phase_alignment = 1.0 - (phase_distance(entry_phase, orbital_phase) / math.pi)
    phase_alignment = max(0.0, min(1.0, phase_alignment))

    max_drift = float(CHANNEL_PARAMS[idx].max_drift or math.pi)
    identity_attractor_score = 1.0 - min(phase_distance(entry_phase, identity_phase) / max(max_drift, 1e-6), 1.0)
    identity_attractor_score = max(0.0, min(1.0, identity_attractor_score))

    sequence = _loop_sequence(channel, kind=kind)
    trajectory = _trajectory_for(channel, kind=kind, entry_phase=entry_phase, phases=phases, identity_phase=identity_phase, braid_phase=braid_phase)
    loop = create_loop_from_trajectory(
        channel_sequence=sequence,
        phase_trajectory=trajectory,
        loop_type=f"{kind}_{channel}",
    )
    holonomy = HolonomyCalculator().compute_eba_defect(loop, hidden_states=phases)
    defect = float(holonomy.get("defect_magnitude", math.pi) or math.pi)
    eba_quality = 1.0 - min(defect / math.pi, 1.0)
    eba_quality = max(0.0, min(1.0, eba_quality))
    closure_quality = 1.0 - (phase_distance(entry_phase, current_phase) / math.pi)
    closure_quality = max(0.0, min(1.0, closure_quality))

    if kind == "consolidation":
        holonomy_quality = (
            0.40 * eba_quality
            + 0.25 * closure_quality
            + 0.20 * identity_attractor_score
            + 0.15 * phase_alignment
        )
    else:
        holonomy_quality = 0.55 * eba_quality + 0.45 * closure_quality

    return {
        "entry_phase": float(entry_phase),
        "current_phase": float(current_phase),
        "orbital_phase": float(orbital_phase),
        "identity_phase": float(identity_phase),
        "phase_alignment": float(phase_alignment),
        "identity_attractor_score": float(identity_attractor_score),
        "closure_quality": float(closure_quality),
        "eba_quality": float(eba_quality),
        "holonomy_quality": float(max(0.0, min(1.0, holonomy_quality))),
        "holonomy_defect": defect,
        "loop_coherent": bool(holonomy.get("is_coherent", False)),
        "loop_type": f"{kind}_{channel}",
    }


def compute_retrieval_holonomy(channel: str, *, entry_phase: float, holder: Any, orbital: Dict[str, Any]) -> Dict[str, Any]:
    return compute_holonomic_profile(channel, entry_phase=entry_phase, holder=holder, orbital=orbital, kind="retrieval")


def compute_consolidation_holonomy(channel: str, *, entry_phase: float, holder: Any, orbital: Dict[str, Any]) -> Dict[str, Any]:
    return compute_holonomic_profile(channel, entry_phase=entry_phase, holder=holder, orbital=orbital, kind="consolidation")


__all__ = [
    "CHANNEL_INDEX",
    "wrap_phase",
    "phase_distance",
    "current_orbital_phase",
    "sector_snapshot",
    "state_phases",
    "compute_retrieval_holonomy",
    "compute_consolidation_holonomy",
]
