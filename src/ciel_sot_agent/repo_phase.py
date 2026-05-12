"""Repository phase state and synchronisation report builder.

Models each repository as a phase-carrying identity with a complex spin,
mass, and role.  Exposes ``build_sync_report`` which loads the repository
registry and coupling map, computes the weighted Euler vector and closure
defect, and returns a machine-readable synchronisation report.
"""
from __future__ import annotations

import cmath
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class RepositoryState:
    key: str
    identity: str
    phi: float
    spin: float
    mass: float
    role: str
    upstream: str


def load_registry(path: str | Path) -> dict[str, RepositoryState]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    repos = data.get('repositories', [])
    out: dict[str, RepositoryState] = {}
    for item in repos:
        state = RepositoryState(
            key=str(item['key']),
            identity=str(item['identity']),
            phi=float(item['phi']),
            spin=float(item['spin']),
            mass=float(item['mass']),
            role=str(item['role']),
            upstream=str(item['upstream']),
        )
        out[state.key] = state
    return out


def load_couplings(path: str | Path) -> dict[str, dict[str, float]]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    raw = data.get('couplings', {})
    return {
        str(k): {str(kk): float(vv) for kk, vv in vv_map.items()}
        for k, vv_map in raw.items()
    }


def weighted_euler_vector(states: Iterable[RepositoryState]) -> complex:
    total = 0j
    for state in states:
        total += state.mass * cmath.exp(1j * state.phi)
    return total


def weighted_euler_vector_numpy(states: Iterable[RepositoryState]) -> complex:
    """Vectorized weighted Euler sum for larger state batches."""
    states = list(states)
    if not states:
        return 0j
    import numpy as np

    mass = np.array([max(0.0, s.mass) for s in states], dtype=float)
    phi = np.array([s.phi for s in states], dtype=float)
    vec = np.sum(mass * np.exp(1j * phi))
    return complex(vec)


def closure_defect(states: Iterable[RepositoryState]) -> float:
    states = list(states)
    total_mass = sum(max(0.0, s.mass) for s in states)
    if total_mass <= 0.0:
        return 1.0
    vec = weighted_euler_vector(states)
    return max(0.0, min(1.0, 1.0 - abs(vec) / total_mass))


def euler_residual(states: Iterable[RepositoryState]) -> float:
    """Normalize the Euler closure residual to [0, 1]."""
    states = list(states)
    if not states:
        return 1.0
    total_mass = sum(max(0.0, s.mass) for s in states)
    if total_mass <= 0.0:
        return 1.0
    vec = weighted_euler_vector_numpy(states)
    return max(0.0, min(1.0, abs(vec) / total_mass))


def pairwise_tension_matrix(
    states: dict[str, RepositoryState],
    couplings: dict[str, dict[str, float]],
) -> list[list[float]]:
    """Build a dense pairwise tension matrix aligned to the sorted state keys."""
    keys = sorted(states.keys())
    n = len(keys)
    if n == 0:
        return []
    index = {k: i for i, k in enumerate(keys)}
    mat = [[0.0] * n for _ in range(n)]
    for src, neighbors in couplings.items():
        i = index.get(src)
        if i is None:
            continue
        for dst, coupling in neighbors.items():
            j = index.get(dst)
            if j is None:
                continue
            if i == j:
                continue
            mat[i][j] = pairwise_tension(states[src], states[dst], float(coupling))
    return mat


def j_repo(
    states: Iterable[RepositoryState],
    couplings: dict[str, dict[str, float]] | None = None,
) -> float:
    """Compact repo-level cost functional combining closure and pairwise tension."""
    states = list(states)
    if not states:
        return 1.0
    defect = closure_defect(states)
    if not couplings:
        return float(defect)
    state_map = {s.key: s for s in states}
    tensions = all_pairwise_tensions(state_map, couplings)
    if not tensions:
        return float(defect)
    mean_tension = sum(float(row["tension"]) for row in tensions) / len(tensions)
    max_tension = max(float(row["tension"]) for row in tensions)
    return float(max(0.0, min(1.0, 0.55 * defect + 0.30 * mean_tension + 0.15 * max_tension)))


def pairwise_tension(a: RepositoryState, b: RepositoryState, coupling: float) -> float:
    return float(coupling) * (1.0 - math.cos(b.phi - a.phi))


def all_pairwise_tensions(
    states: dict[str, RepositoryState],
    couplings: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for src, neighbors in couplings.items():
        if src not in states:
            continue
        for dst, k in neighbors.items():
            if dst not in states:
                continue
            rows.append(
                {
                    'source': src,
                    'target': dst,
                    'coupling': float(k),
                    'tension': pairwise_tension(states[src], states[dst], float(k)),
                }
            )
    rows.sort(key=lambda x: (x['source'], x['target']))
    return rows


def build_sync_report(
    registry_path: str | Path,
    couplings_path: str | Path,
) -> dict[str, Any]:
    states = load_registry(registry_path)
    couplings = load_couplings(couplings_path)
    defect = closure_defect(states.values())
    residual = euler_residual(states.values())
    vec = weighted_euler_vector(states.values())
    tensions = all_pairwise_tensions(states, couplings)
    tension_values = [float(row["tension"]) for row in tensions]
    return {
        'repository_count': len(states),
        'weighted_euler_vector': {
            'real': vec.real,
            'imag': vec.imag,
            'abs': abs(vec),
        },
        'closure_defect': defect,
        'euler_residual': residual,
        'pairwise_tensions': tensions,
        'mean_pairwise_tension': sum(tension_values) / len(tension_values) if tension_values else 0.0,
        'max_pairwise_tension': max(tension_values) if tension_values else 0.0,
        'j_repo': j_repo(states.values(), couplings),
    }
