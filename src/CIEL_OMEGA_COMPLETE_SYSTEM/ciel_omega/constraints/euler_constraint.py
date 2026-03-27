
"""Unified multi-sector Euler/EBA/semantic closure for CIEL/Ω.

This module now supports four phase sectors:
- memory
- core
- vocabulary / semantic
- affect

It also provides active feedback with rollback-safe helpers so the same
constraint can be used both as a metric and as a runtime regulator.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Mapping, Sequence
import hashlib
import math
import numpy as np

try:
    from ..phase_equation_of_motion import euler_constraint_violation, phase_sector  # type: ignore
except Exception:
    def euler_constraint_violation(phases: Sequence[float]) -> float:
        phases = np.asarray(phases, dtype=float)
        if phases.size == 0:
            return 0.0
        return float(abs(np.mean(np.exp(1j * phases))))

    def phase_sector(phases: Sequence[float]) -> float:
        phases = np.asarray(phases, dtype=float)
        if phases.size == 0:
            return 0.0
        return float(np.angle(np.mean(np.exp(1j * phases))))


@dataclass
class EulerConstraintReport:
    memory_phase_vector: list[float]
    core_phase_vector: list[float]
    vocabulary_phase_vector: list[float]
    affect_phase_vector: list[float]
    unified_phase_vector: list[float]
    memory_eba_mean_defect: float
    memory_eba_max_defect: float
    memory_eba_coherent_fraction: float
    sector_euler_violation: Dict[str, float]
    sector_phase_sector: Dict[str, float]
    pairwise_phase_tension: Dict[str, float]
    core_euler_violation: float
    core_phase_sector: float
    unified_euler_violation: float
    unified_phase_sector: float
    closure_score: float
    target_phase: float = 0.0
    regulation_strength: float = 0.0
    rolled_back: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


DEFAULT_SECTOR_WEIGHTS: Dict[str, float] = {
    'memory': 1.00,
    'core': 1.00,
    'vocabulary': 1.15,
    'semantic': 1.20,
    'affect': 1.10,
}


def _wrap(phi: float) -> float:
    return float(phi % (2.0 * math.pi))


def _circ_mean(phases: np.ndarray) -> float:
    if phases.size == 0:
        return 0.0
    return float(np.angle(np.mean(np.exp(1j * phases))))


def _safe_angle_mean(field: np.ndarray) -> float:
    angles = np.angle(field)
    return _wrap(_circ_mean(angles.ravel()))


def _build_core_phase_vector(core: Any) -> np.ndarray:
    phase_i = _safe_angle_mean(np.asarray(core.I_field))
    phase_s = _safe_angle_mean(np.asarray(core.S_field))
    phase_tau = _wrap(float(np.mean(np.asarray(core.tau_field))))
    lambda_mean = float(np.mean(np.asarray(core.Lambda0_field)))
    phase_lambda = _wrap(math.pi * (1.0 + math.tanh(lambda_mean)))
    return np.array([phase_i, phase_s, phase_tau, phase_lambda], dtype=float)


def _canonical_id_to_phase(canonical_id: str) -> float:
    h = hashlib.sha256(canonical_id.encode('utf-8')).digest()
    value = int.from_bytes(h[:8], 'big') / float(2**64)
    return _wrap(2.0 * math.pi * value)


def _priority_weight(record: Mapping[str, Any]) -> float:
    try:
        return float(record.get('priority', 1.0))
    except Exception:
        return 1.0


def _build_vocabulary_phase_vector(semantic_records: Sequence[Mapping[str, Any]] | None = None,
                                   vocabulary_metrics: Mapping[str, Any] | None = None) -> np.ndarray:
    phases: list[float] = []
    if semantic_records:
        for rec in semantic_records:
            cid = str(rec.get('canonical_id') or '')
            if not cid:
                continue
            base = _canonical_id_to_phase(cid)
            w = _priority_weight(rec)
            # repeat by quantized weight so priorities influence the circular mean
            reps = max(1, int(round(2 * w)))
            phases.extend([base] * reps)
    if not phases and vocabulary_metrics:
        text = str(vocabulary_metrics.get('semantic_key', '') or '')
        if text:
            phases.append(_canonical_id_to_phase(text))
    return np.asarray(phases, dtype=float)


def _build_affect_phase_vector(metadata: Mapping[str, Any] | None = None) -> np.ndarray:
    metadata = metadata or {}
    salience = float(metadata.get('salience', 0.5))
    confidence = float(metadata.get('confidence', 0.5))
    novelty = float(metadata.get('novelty', 0.5))
    valence = float(metadata.get('valence', salience - 0.5))
    phases = [
        _wrap(2.0 * math.pi * salience),
        _wrap(2.0 * math.pi * confidence),
        _wrap(2.0 * math.pi * novelty),
        _wrap(math.pi * (1.0 + math.tanh(valence))),
    ]
    return np.asarray(phases, dtype=float)


def _memory_stats(eba_results: Mapping[str, Any]) -> tuple[float, float, float]:
    defects: list[float] = []
    coherences: list[float] = []
    for v in eba_results.values():
        defect = getattr(v, 'defect_magnitude', None)
        coherent = getattr(v, 'is_coherent', None)
        if defect is None and isinstance(v, Mapping):
            defect = v.get('defect_magnitude', 0.0)
            coherent = v.get('is_coherent', True)
        defects.append(float(defect or 0.0))
        coherences.append(1.0 if bool(coherent) else 0.0)
    if not defects:
        return 0.0, 0.0, 1.0
    return float(np.mean(defects)), float(np.max(defects)), float(np.mean(coherences))


def _sector_metrics(phase_vectors: Mapping[str, np.ndarray]) -> tuple[Dict[str, float], Dict[str, float]]:
    violations: Dict[str, float] = {}
    sectors: Dict[str, float] = {}
    for name, vec in phase_vectors.items():
        violations[name] = float(euler_constraint_violation(vec)) if vec.size else 0.0
        sectors[name] = float(phase_sector(vec)) if vec.size else 0.0
    return violations, sectors


def _pairwise_tension(sectors: Mapping[str, float], weights: Mapping[str, float] | None = None) -> Dict[str, float]:
    weights = weights or DEFAULT_SECTOR_WEIGHTS
    keys = list(sectors.keys())
    out: Dict[str, float] = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            delta = math.atan2(math.sin(sectors[a] - sectors[b]), math.cos(sectors[a] - sectors[b]))
            out[f'{a}:{b}'] = float(abs(delta) * 0.5 * (weights.get(a, 1.0) + weights.get(b, 1.0)))
    return out


def circular_target_phase(sector_phase_sector: Mapping[str, float],
                          sector_euler_violation: Mapping[str, float],
                          sector_weights: Mapping[str, float] | None = None) -> float:
    sector_weights = dict(DEFAULT_SECTOR_WEIGHTS | dict(sector_weights or {}))
    vec = 0j
    for name, phi in sector_phase_sector.items():
        # high weight and low violation should dominate the target
        w = sector_weights.get(name, 1.0) / (1e-6 + sector_euler_violation.get(name, 0.0) + 0.1)
        vec += w * np.exp(1j * phi)
    if abs(vec) < 1e-12:
        return 0.0
    return _wrap(float(np.angle(vec)))


def regulation_strength(report_or_violation: EulerConstraintReport | float,
                        closure_score: float | None = None) -> float:
    if isinstance(report_or_violation, EulerConstraintReport):
        violation = report_or_violation.unified_euler_violation
        closure = report_or_violation.closure_score
    else:
        violation = float(report_or_violation)
        closure = float(closure_score if closure_score is not None else 0.0)
    strength = 0.35 * violation + 0.15 * (1.0 - closure)
    return float(np.clip(strength, 0.0, 0.35))


def evaluate_unified_euler_constraint(memory: Any,
                                      core: Any,
                                      eba_results: Mapping[str, Any],
                                      semantic_records: Sequence[Mapping[str, Any]] | None = None,
                                      vocabulary_metrics: Mapping[str, Any] | None = None,
                                      metadata: Mapping[str, Any] | None = None,
                                      sector_weights: Mapping[str, float] | None = None) -> EulerConstraintReport:
    sector_weights = dict(DEFAULT_SECTOR_WEIGHTS | dict(sector_weights or {}))
    memory_phase_vector = np.asarray(getattr(memory.state, 'phases', []), dtype=float)
    core_phase_vector = _build_core_phase_vector(core)
    vocabulary_phase_vector = _build_vocabulary_phase_vector(semantic_records, vocabulary_metrics)
    affect_phase_vector = _build_affect_phase_vector(metadata)

    phase_vectors = {
        'memory': memory_phase_vector,
        'core': core_phase_vector,
        'vocabulary': vocabulary_phase_vector,
        'affect': affect_phase_vector,
    }

    unified_chunks = [vec for vec in phase_vectors.values() if vec.size]
    unified_phase_vector = np.concatenate(unified_chunks) if unified_chunks else np.asarray([], dtype=float)

    memory_eba_mean_defect, memory_eba_max_defect, memory_eba_coherent_fraction = _memory_stats(eba_results)
    sector_euler_violation, sector_phase_sector = _sector_metrics(phase_vectors)
    pairwise_phase_tension = _pairwise_tension(sector_phase_sector, sector_weights)

    core_eps = sector_euler_violation['core']
    core_sector = sector_phase_sector['core']
    unified_eps = float(euler_constraint_violation(unified_phase_vector)) if unified_phase_vector.size else 0.0
    unified_sector = float(phase_sector(unified_phase_vector)) if unified_phase_vector.size else 0.0

    closure_penalty = (
        0.35 * unified_eps +
        0.20 * memory_eba_mean_defect / math.pi +
        0.15 * (1.0 - memory_eba_coherent_fraction) +
        0.20 * float(np.mean(list(pairwise_phase_tension.values()) or [0.0])) / math.pi +
        0.10 * float(np.mean([v for k, v in sector_euler_violation.items() if k != 'memory'] or [0.0]))
    )
    closure_score = float(np.clip(1.0 - closure_penalty, 0.0, 1.0))
    target_phase = circular_target_phase(sector_phase_sector, sector_euler_violation, sector_weights)
    strength = regulation_strength(unified_eps, closure_score)

    return EulerConstraintReport(
        memory_phase_vector=memory_phase_vector.tolist(),
        core_phase_vector=core_phase_vector.tolist(),
        vocabulary_phase_vector=vocabulary_phase_vector.tolist(),
        affect_phase_vector=affect_phase_vector.tolist(),
        unified_phase_vector=unified_phase_vector.tolist(),
        memory_eba_mean_defect=memory_eba_mean_defect,
        memory_eba_max_defect=memory_eba_max_defect,
        memory_eba_coherent_fraction=memory_eba_coherent_fraction,
        sector_euler_violation=sector_euler_violation,
        sector_phase_sector=sector_phase_sector,
        pairwise_phase_tension=pairwise_phase_tension,
        core_euler_violation=core_eps,
        core_phase_sector=core_sector,
        unified_euler_violation=unified_eps,
        unified_phase_sector=unified_sector,
        closure_score=closure_score,
        target_phase=target_phase,
        regulation_strength=strength,
        rolled_back=False,
    )


def _apply_phase_pull(values: np.ndarray, target: float, strength: float) -> np.ndarray:
    if values.size == 0:
        return values
    delta = np.angle(np.exp(1j * (target - values)))
    return np.mod(values + strength * delta, 2.0 * math.pi)


def apply_active_euler_feedback(memory: Any,
                                core: Any,
                                report: EulerConstraintReport,
                                *,
                                semantic_records: Sequence[Mapping[str, Any]] | None = None,
                                vocabulary_metrics: Mapping[str, Any] | None = None,
                                metadata: Mapping[str, Any] | None = None,
                                sector_weights: Mapping[str, float] | None = None) -> tuple[EulerConstraintReport, bool]:
    """Actively pull sectors toward the weighted Euler target.

    Returns updated_report, rolled_back.
    Rollback happens if the feedback step worsens unified closure.
    """
    target = report.target_phase
    strength = report.regulation_strength

    # snapshots for rollback
    memory_phases_before = np.asarray(memory.state.phases, dtype=float).copy()
    identity_phase_before = float(getattr(memory.identity_field, 'phase', 0.0))
    core_I_before = np.asarray(core.I_field).copy()
    core_S_before = np.asarray(core.S_field).copy()
    core_tau_before = np.asarray(core.tau_field).copy()

    # apply to memory sector
    new_mem = _apply_phase_pull(memory_phases_before, target, strength)
    memory.state.phases = list(map(float, new_mem))
    if hasattr(memory.identity_field, 'phase'):
        memory.identity_field.phase = _wrap(identity_phase_before + strength * math.atan2(math.sin(target - identity_phase_before), math.cos(target - identity_phase_before)))

    # apply to core phases while preserving amplitudes
    for field_name in ('I_field', 'S_field'):
        field = np.asarray(getattr(core, field_name))
        amp = np.abs(field)
        ph = np.angle(field)
        ph2 = _apply_phase_pull(ph, target, 0.5 * strength)
        setattr(core, field_name, amp * np.exp(1j * ph2))
    core.tau_field = np.asarray(core_tau_before) + 0.10 * strength * np.sin(target - np.asarray(core_tau_before))

    # recompute post-step report
    eba_results = {
        f'm{i}': {'defect_magnitude': abs(math.atan2(math.sin(p - target), math.cos(p - target))), 'is_coherent': abs(math.atan2(math.sin(p - target), math.cos(p - target))) < 0.35}
        for i, p in enumerate(np.asarray(memory.state.phases, dtype=float))
    }
    updated = evaluate_unified_euler_constraint(
        memory,
        core,
        eba_results,
        semantic_records=semantic_records,
        vocabulary_metrics=vocabulary_metrics,
        metadata=metadata,
        sector_weights=sector_weights,
    )

    rolled_back = False
    if updated.unified_euler_violation > report.unified_euler_violation:
        # rollback if worse
        rolled_back = True
        memory.state.phases = list(map(float, memory_phases_before))
        if hasattr(memory.identity_field, 'phase'):
            memory.identity_field.phase = identity_phase_before
        core.I_field = core_I_before
        core.S_field = core_S_before
        core.tau_field = core_tau_before
        updated = report
    updated.rolled_back = rolled_back
    return updated, rolled_back
