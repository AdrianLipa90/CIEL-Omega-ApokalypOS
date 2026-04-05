"""Holonomic phase normalizer for the CIEL integration kernel.

Provides circular-arithmetic utilities (phase wrapping, circular barycenter,
circular distance) and the HolonomicNormalizer class that applies weighted
renormalization across a map of named phase-carrying nodes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, MutableMapping


def wrap(angle: float) -> float:
    """Wrap angle to (-pi, pi]."""
    two_pi = 2.0 * math.pi
    value = (angle + math.pi) % two_pi - math.pi
    if value <= -math.pi:
        return value + two_pi
    return value


def circular_barycenter(phases: Iterable[float], weights: Iterable[float]) -> float:
    xs = 0.0
    ys = 0.0
    for phi, w in zip(phases, weights):
        xs += w * math.cos(phi)
        ys += w * math.sin(phi)
    if xs == 0.0 and ys == 0.0:
        return 0.0
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
    if norm <= 0.0:
        return dict(couplings)
    return {k: float(v) / norm for k, v in couplings.items()}


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
        couplings = _get(X, "couplings", {})
        tensions = list(callbacks.all_pairwise_tensions(_get(X, "repo_states"), couplings))
        T_mean = sum(float(t.get("tension", 0.0)) for t in tensions) / len(tensions) if tensions else 0.0

        final = _get(X, "orbital_final", {})
        E_phi = float(_get(final, "closure_penalty", 0.0))

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
            10.0 * float(_get(distortion, "lie", 0.0))
            + 8.0 * float(_get(distortion, "omit", 0.0))
            + 12.0 * float(_get(distortion, "hallucinate", 0.0))
            + 3.0 * soft_dist
        )

        objects = list(_get(X, "objects", []))
        B_placeholder = float(callbacks.compute_placeholder_penalty(objects))
        B_demo = float(callbacks.compute_demo_legacy_penalty(objects))
        B_seam = float(callbacks.compute_semantic_execution_seam_penalty(X))

        J_prev = _get(X, "J", None)
        X.J = (
            1.2 * D_repo
            + 1.0 * T_mean
            + 1.1 * E_phi
            + 1.4 * d_affect
            + 1.0 * d_memory
            + 1.3 * B_seam
            + 1.5 * P_dist
            + 0.7 * B_placeholder
            + 0.8 * B_demo
        )

        phi_core = float(_get(core, "phi", 0.0))
        phi_aff = float(_get(affect, "phi", 0.0))
        _set(affect, "phi", phi_aff - 0.18 * wrap(phi_aff - phi_core))

        excess_affect = max(0.0, d_affect - 0.18)
        aff_amp = float(_get(affect, "amplitude", 1.0))
        aff_floor = float(_get(affect, "min_amplitude_floor", 0.05))
        aff_amp *= (1.0 - 0.18 * excess_affect)
        _set(affect, "amplitude", max(aff_amp, aff_floor))

        lobes = list(_get(memory, "lobes", [0.0, 0.0]))
        weights = list(_get(memory, "lobe_weights", [0.5, 0.5]))
        phi_star = circular_barycenter(lobes, weights)
        lobes[0] = lobes[0] - 0.14 * wrap(lobes[0] - phi_star)
        lobes[1] = lobes[1] - 0.14 * wrap(lobes[1] - phi_star)
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
            updated_couplings[(i, j)] *= (qi * qj) / (1.0 + 0.6 * Tij)

        updated_couplings = symmetrize_couplings(updated_couplings)
        updated_couplings = clip_couplings(updated_couplings, lo=0.0, hi=float(_get(X, "max_coupling", 1.0)))
        updated_couplings = renormalize_couplings(updated_couplings, target_norm="l1")
        _set(X, "couplings", updated_couplings)

        if hard_dist > 0.0 or D_repo > 0.18 or E_phi > 6.10 or d_affect > 0.32:
            _set(X, "mode", "safe")
            _set(X, "allow_writeback", False)
        elif soft_dist > 0.0 or D_repo > 0.08 or E_phi > 5.85:
            _set(X, "mode", "standard")
            _set(X, "allow_writeback", True)
        else:
            _set(X, "mode", "deep")
            _set(X, "allow_writeback", True)

        X = callbacks.recompute_manifests_and_bridge(X)

        memory_after = _sector(X, "memory")
        memory_lobes_after = list(_get(memory_after, "lobes", [0.0, 0.0]))
        memory_split = circular_distance(memory_lobes_after[0], memory_lobes_after[1])
        thresholds = _get(X, "thresholds", {})
        seam_ok = float(_get(thresholds, "seam_ok", 0.15))

        stable = (
            J_prev is not None
            and abs(float(X.J) - float(J_prev)) < eps
            and float(_get(_sector(X, "affect"), "decoherence", 0.0)) < 0.22
            and memory_split < 0.10
            and B_seam < seam_ok
            and _get(X, "mode") != "safe"
        )
        if stable:
            break

    return X
