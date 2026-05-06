"""Holonomic phase normalizer for the CIEL integration kernel.

Provides circular-arithmetic utilities (phase wrapping, circular barycenter,
circular distance) and the HolonomicNormalizer class that applies weighted
renormalization across a map of named phase-carrying nodes.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, MutableMapping

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# J-function (global cost functional) component weights
# ---------------------------------------------------------------------------
_W_D_REPO = 1.2       # closure-defect contribution
_W_T_MEAN = 1.0       # mean pairwise tension
_W_E_PHI = 1.1        # orbital closure penalty
_W_D_AFFECT = 1.4     # affect-sector decoherence
_W_D_MEMORY = 1.0     # memory-sector decoherence
_W_B_SEAM = 1.3       # semantic-execution seam penalty
_W_P_DIST = 1.5       # distortion penalty (weighted sum of lie/omit/hallucinate)
_W_B_PLACEHOLDER = 0.7  # placeholder-object penalty
_W_B_DEMO = 0.8       # demo-legacy penalty

# Metatime Intention Operator — universal topological coupler (I₀ = 0.009).
# Adds a holonomic correction term: I₀ × (D_repo + E_phi + d_affect).
# Physical basis: Berry phase γᵢ=π for all fermions; I₀ is the scalar coupling
# between the topological charge (Chern class) and the global phase coherence.
_I0_TOPOLOGICAL = 0.009

# Distortion sub-weights (lie/omit/hallucinate carry higher ethical cost)
_W_LIE = 10.0
_W_OMIT = 8.0
_W_HALLUCINATE = 12.0
_W_SMOOTH = 3.0        # soft / smoothing distortion

# Sector-update rates
_AFFECT_PHASE_RATE = 0.18    # rate at which affect phase tracks core phase
_AFFECT_AMP_DECAY = 0.18     # amplitude decay coefficient per unit excess decoherence
_AFFECT_DECOHERENCE_FLOOR = 0.18  # excess decoherence threshold
_MEMORY_LOBE_RATE = 0.14     # rate at which memory lobes converge to their barycenter

# Coupling renormalization damping
_COUPLING_TENSION_DAMP = 0.6  # damping factor for tension-based coupling update

# 3-body (Wᵢⱼₖ) weight — lower than pairwise _W_T_MEAN to avoid double-counting
_W_T3 = 0.4

# Mode-selection thresholds — expressed in ψ_mode space (see phase_control.mode_norm).
# ψ = (1 − ci) + γ · penalty / penalty_max   where γ=0.15, penalty_max=8.0
# Boundaries imported from phase_control so there is exactly one source of truth.
from ciel_omega.orbital.phase_control import (
    mode_norm as _mode_norm,
    coherence_index_from_snapshot as _ci_from_snap,
    _PSI_DEEP     as _PSI_DEEP,
    _PSI_STANDARD as _PSI_STANDARD,
)

_SAFE_HARD_DIST_THRESH = 0.0   # any hard distortion forces safe regardless of ψ
_SAFE_D_REPO_THRESH    = 0.18  # repo closure defect → safe
_SAFE_D_AFFECT_THRESH  = 0.32  # affect decoherence  → safe
_STD_D_REPO_THRESH     = 0.08  # repo closure defect → standard (below safe)

# Convergence criteria
_STABLE_D_AFFECT_MAX = 0.30    # affect decoherence must be below this to converge (non-safe)
_STABLE_MEMORY_SPLIT_MAX = 0.10  # max circular distance between memory lobes to converge
# Affect decoherence decay: when amplitude drops below floor ratio, decoherence couples to amplitude.
# Physical basis: low amplitude = quiescent affective state → lower decoherence.
_AFFECT_DECOHERENCE_DECAY = 0.06  # per-step decay when amplitude is at floor


def wrap(angle: float) -> float:
    """Wrap angle to (-pi, pi]."""
    two_pi = 2.0 * math.pi
    value = (angle + math.pi) % two_pi - math.pi
    if value <= -math.pi:
        return value + two_pi
    return value


_H_CLIP = 1e-9  # Heisenberg soft clip: ΔxΔp ≥ ℏ/2 — prevents degenerate phase collapse


def circular_barycenter(phases: Iterable[float], weights: Iterable[float]) -> float:
    xs = 0.0
    ys = 0.0
    for phi, w in zip(phases, weights):
        xs += w * math.cos(phi)
        ys += w * math.sin(phi)
    if abs(xs) < _H_CLIP and abs(ys) < _H_CLIP:
        xs = _H_CLIP  # soft clip — phase undefined but non-zero
    return math.atan2(ys, xs)


def circular_distance(a: float, b: float) -> float:
    return abs(wrap(a - b))


def symmetrize_couplings(couplings: Mapping[tuple[str, str], float]) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    seen: set[tuple[str, str]] = set()
    for i, j in couplings.keys():
        if (i, j) in seen or (j, i) in seen:
            continue
        a = float(couplings.get((i, j), 0.0))
        b = float(couplings.get((j, i), 0.0))
        mean = 0.5 * (a + b)
        out[(i, j)] = mean
        out[(j, i)] = mean
        seen.add((i, j))
        seen.add((j, i))
    return out


def clip_couplings(
    couplings: Mapping[tuple[str, str], float],
    *,
    lo: float = 0.0,
    hi: float = 1.0,
) -> dict[tuple[str, str], float]:
    return {k: min(hi, max(lo, float(v))) for k, v in couplings.items()}


def renormalize_couplings(
    couplings: Mapping[tuple[str, str], float],
    *,
    target_norm: str = "l1",
) -> dict[tuple[str, str], float]:
    if not couplings:
        return {}
    values = [abs(float(v)) for v in couplings.values()]
    if target_norm == "l1":
        norm = sum(values)
    elif target_norm == "l2":
        norm = math.sqrt(sum(v * v for v in values))
    else:
        raise ValueError(f"unsupported target_norm={target_norm!r}")
    if norm <= _H_CLIP:
        return dict(couplings)
    return {k: float(v) / norm for k, v in couplings.items()}


def triplet_tension(phi_i: float, phi_j: float, phi_k: float,
                    K_ij: float, K_jk: float, K_ik: float) -> float:
    """W_ijk — geometric mean of three pairwise tensions.

    Physical basis: Metatime white-thread holonomy Wᵢⱼₖ for composite states
    (mesons, baryons). The geometric mean preserves scale invariance and collapses
    to zero when any single leg has zero coupling.
    """
    t_ij = K_ij * (1.0 - math.cos(phi_j - phi_i))
    t_jk = K_jk * (1.0 - math.cos(phi_k - phi_j))
    t_ik = K_ik * (1.0 - math.cos(phi_k - phi_i))
    return (t_ij * t_jk * t_ik) ** (1.0 / 3.0)


@dataclass
class HolonomicCallbacks:
    closure_defect: Callable[[Any], float]
    all_pairwise_tensions: Callable[[Any, Mapping[tuple[str, str], float]], Iterable[Mapping[str, float]]]
    compute_placeholder_penalty: Callable[[Iterable[Any]], float]
    compute_demo_legacy_penalty: Callable[[Iterable[Any]], float]
    compute_semantic_execution_seam_penalty: Callable[[Any], float]
    object_break_penalty: Callable[[Any], float]
    seam_local_penalty: Callable[[Any, Any], float]
    local_tension: Callable[[Any, str, str], float]
    recompute_manifests_and_bridge: Callable[[Any], Any]
    load_full_state: Callable[[Any], Any] = lambda x: x
    # Optional: triplet tensions for composite objects (Metatime W_ijk holonomy).
    # Signature matches all_pairwise_tensions but returns triplet dicts.
    # None = disabled (backwards compatible).
    all_triplet_tensions: Callable[[Any, Mapping[tuple[str, str], float]], Iterable[Mapping[str, float]]] | None = None


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _set(obj: Any, key: str, value: Any) -> None:
    if isinstance(obj, MutableMapping):
        obj[key] = value
    else:
        setattr(obj, key, value)


def _sector(X: Any, name: str) -> Any:
    sectors = _get(X, "sectors")
    if sectors is None:
        raise KeyError("state has no sectors")
    return sectors[name]


def _select_control_mode(
    hard_dist: float,
    soft_dist: float,
    D_repo: float,
    E_phi: float,
    d_affect: float,
    ci: float = 1.0,
) -> tuple[str, bool]:
    """Return ``(mode, allow_writeback)`` based on distortion and coherence levels.

    Mode boundaries are unified with phase_control via ψ_mode norm so that
    holonomic_normalizer and orbital_bridge always agree on thresholds.

    * ``"safe"``     — hard distortion, repo/affect defect above critical level,
                       or ψ ≥ _PSI_STANDARD.  Write-back disabled.
    * ``"standard"`` — soft distortion, mild repo defect, or _PSI_DEEP ≤ ψ < _PSI_STANDARD.
                       Write-back allowed with caution.
    * ``"deep"``     — ψ < _PSI_DEEP and no distortion.  Full write-back.
    """
    psi = _mode_norm(ci, E_phi)
    if (
        hard_dist > _SAFE_HARD_DIST_THRESH
        or D_repo > _SAFE_D_REPO_THRESH
        or d_affect > _SAFE_D_AFFECT_THRESH
        or psi >= _PSI_STANDARD
    ):
        return "safe", False
    if soft_dist > 0.0 or D_repo > _STD_D_REPO_THRESH or psi >= _PSI_DEEP:
        return "standard", True
    return "deep", True


def holonomic_system_normalizer_v2(
    state: Any,
    callbacks: HolonomicCallbacks,
    *,
    max_iter: int = 24,
    eps: float = 1e-4,
) -> Any:
    X = callbacks.load_full_state(state)

    for _step in range(max_iter):
        D_repo = float(callbacks.closure_defect(_get(X, "repo_states")))

        # Cᵢ suppression penalty — sectors with negative suppression (Metatime d-quark analogue)
        # contribute additional closure defect. Normalized by 1e-3 (Cᵢ is in units of tens).
        _suppression_penalty = 0.0
        for _sec_name in ("constraints", "fields", "runtime", "memory", "bridge", "vocabulary"):
            try:
                _C_i = float(_get(_sector(X, _sec_name), "suppression", 0.0))
                if _C_i < 0.0:
                    _suppression_penalty += abs(_C_i) * 1e-3
            except (KeyError, TypeError):
                pass
        D_repo_eff = D_repo + _suppression_penalty

        couplings = _get(X, "couplings", {})
        tensions = list(callbacks.all_pairwise_tensions(_get(X, "repo_states"), couplings))
        T_mean = sum(float(t.get("tension", 0.0)) for t in tensions) / len(tensions) if tensions else 0.0

        final = _get(X, "orbital_final", {})
        E_phi = float(_get(final, "closure_penalty", 0.0))
        _ci   = _ci_from_snap(final)

        affect = _sector(X, "affect")
        memory = _sector(X, "memory")
        core = _sector(X, "core")
        vocabulary = _sector(X, "vocabulary")

        d_affect = float(_get(affect, "decoherence", 0.0))
        d_memory = float(_get(memory, "decoherence", 0.0))

        distortion = _get(X, "distortion", {})
        hard_dist = float(_get(distortion, "lie", 0.0)) + float(_get(distortion, "omit", 0.0)) + float(_get(distortion, "hallucinate", 0.0))
        soft_dist = float(_get(distortion, "smooth", 0.0))

        P_dist = (
            _W_LIE * float(_get(distortion, "lie", 0.0))
            + _W_OMIT * float(_get(distortion, "omit", 0.0))
            + _W_HALLUCINATE * float(_get(distortion, "hallucinate", 0.0))
            + _W_SMOOTH * soft_dist
        )

        objects = list(_get(X, "objects", []))
        B_placeholder = float(callbacks.compute_placeholder_penalty(objects))
        B_demo = float(callbacks.compute_demo_legacy_penalty(objects))
        B_seam = float(callbacks.compute_semantic_execution_seam_penalty(X))

        T3_mean = 0.0
        if callbacks.all_triplet_tensions is not None:
            triplets = list(callbacks.all_triplet_tensions(_get(X, "repo_states"), couplings))
            T3_mean = sum(float(t.get("tension", 0.0)) for t in triplets) / max(len(triplets), 1)

        J_prev = _get(X, "J", None)
        X.J = (
            _W_D_REPO * D_repo_eff
            + _W_T_MEAN * T_mean
            + _W_T3 * T3_mean
            + _W_E_PHI * E_phi
            + _W_D_AFFECT * d_affect
            + _W_D_MEMORY * d_memory
            + _W_B_SEAM * B_seam
            + _W_P_DIST * P_dist
            + _W_B_PLACEHOLDER * B_placeholder
            + _W_B_DEMO * B_demo
            + _I0_TOPOLOGICAL * (D_repo_eff + E_phi + d_affect)  # holonomic correction
        )

        phi_core = float(_get(core, "phi", 0.0))
        phi_aff = float(_get(affect, "phi", 0.0))
        _set(affect, "phi", phi_aff - _AFFECT_PHASE_RATE * wrap(phi_aff - phi_core))

        excess_affect = max(0.0, d_affect - _AFFECT_DECOHERENCE_FLOOR)
        aff_amp = float(_get(affect, "amplitude", 1.0))
        aff_floor = float(_get(affect, "min_amplitude_floor", 0.05))
        aff_amp *= (1.0 - _AFFECT_AMP_DECAY * excess_affect)
        aff_amp = max(aff_amp, aff_floor)
        _set(affect, "amplitude", aff_amp)
        # Quiescent coupling: when amplitude is at floor, decoherence decays (affective silence).
        if aff_amp <= aff_floor * 1.05:
            new_d = d_affect * (1.0 - _AFFECT_DECOHERENCE_DECAY)
            _set(affect, "decoherence", max(new_d, 0.0))

        lobes = list(_get(memory, "lobes", [0.0, 0.0]))
        weights = list(_get(memory, "lobe_weights", [0.5, 0.5]))
        phi_star = circular_barycenter(lobes, weights)
        lobes[0] = lobes[0] - _MEMORY_LOBE_RATE * wrap(lobes[0] - phi_star)
        lobes[1] = lobes[1] - _MEMORY_LOBE_RATE * wrap(lobes[1] - phi_star)
        _set(memory, "lobes", lobes)

        _set(vocabulary, "phi", 0.0)

        for obj in objects:
            penalty = float(callbacks.object_break_penalty(obj)) + float(callbacks.seam_local_penalty(X, obj))
            current_exec_weight = float(_get(obj, "exec_weight", 1.0))
            _set(obj, "exec_weight", current_exec_weight * math.exp(-penalty))

        updated_couplings: dict[tuple[str, str], float] = dict(couplings)
        quality = _get(X, "quality", {})
        for i, j in list(updated_couplings.keys()):
            qi = float(quality.get(i, 1.0)) if isinstance(quality, Mapping) else 1.0
            qj = float(quality.get(j, 1.0)) if isinstance(quality, Mapping) else 1.0
            Tij = float(callbacks.local_tension(X, i, j))
            updated_couplings[(i, j)] *= (qi * qj) / (1.0 + _COUPLING_TENSION_DAMP * Tij)

        updated_couplings = symmetrize_couplings(updated_couplings)
        updated_couplings = clip_couplings(updated_couplings, lo=0.0, hi=float(_get(X, "max_coupling", 1.0)))
        updated_couplings = renormalize_couplings(updated_couplings, target_norm="l1")
        _set(X, "couplings", updated_couplings)

        mode, allow_writeback = _select_control_mode(hard_dist, soft_dist, D_repo_eff, E_phi, d_affect, ci=_ci)
        _set(X, "mode", mode)
        _set(X, "allow_writeback", allow_writeback)

        X = callbacks.recompute_manifests_and_bridge(X)

        memory_after = _sector(X, "memory")
        memory_lobes_after = list(_get(memory_after, "lobes", [0.0, 0.0]))
        memory_split = circular_distance(memory_lobes_after[0], memory_lobes_after[1])
        thresholds = _get(X, "thresholds", {})
        seam_ok = float(_get(thresholds, "seam_ok", 0.15))

        d_affect_now = float(_get(_sector(X, "affect"), "decoherence", 0.0))
        current_mode = _get(X, "mode")
        j_stable = J_prev is not None and abs(float(X.J) - float(J_prev)) < eps
        # Safe-mode convergence: allowed when J is stable and no hard distortion.
        # Physical basis: safe is a valid protective attractor; blocking it inflates step count.
        safe_stable = j_stable and current_mode == "safe" and hard_dist <= 0.0
        # Normal convergence: J stable, affect quiet, memory coalesced, seam within budget.
        normal_stable = (
            j_stable
            and d_affect_now < _STABLE_D_AFFECT_MAX
            and memory_split < _STABLE_MEMORY_SPLIT_MAX
            and B_seam < seam_ok
            and current_mode != "safe"
        )
        if safe_stable or normal_stable:
            break

    return X
