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


def closure_defect(states: Iterable[RepositoryState]) -> float:
    states = list(states)
    total_mass = sum(max(0.0, s.mass) for s in states)
    if total_mass <= 0.0:
        return 1.0
    vec = weighted_euler_vector(states)
    return max(0.0, min(1.0, 1.0 - abs(vec) / total_mass))


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
    vec = weighted_euler_vector(states.values())
    tensions = all_pairwise_tensions(states, couplings)
    return {
        'repository_count': len(states),
        'weighted_euler_vector': {
            'real': vec.real,
            'imag': vec.imag,
            'abs': abs(vec),
        },
        'closure_defect': defect,
        'pairwise_tensions': tensions,
    }
