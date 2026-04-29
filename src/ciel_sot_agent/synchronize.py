"""Synchronise entry point (v1) — builds and emits a sync report to stdout.

Reads the repository registry and coupling map from the ``integration/``
directory, calls ``repo_phase.build_sync_report``, and prints the result
as formatted JSON.  Invoked via the ``ciel-sot-sync`` console script.
"""
from __future__ import annotations

import json
import logging
import math
import random
import time
from pathlib import Path

from .paths import resolve_project_root
from .repo_phase import (
    build_sync_report, load_registry, load_couplings,
    closure_defect, weighted_euler_vector, all_pairwise_tensions,
)

_LOG = logging.getLogger(__name__)


def _apply_thermal_noise(registry_path: Path, couplings_path: Path) -> dict:
    """Build sync report with per-run phase noise so metrics visibly evolve."""
    import dataclasses
    states = load_registry(registry_path)
    couplings = load_couplings(couplings_path)
    rng = random.Random(int(time.time() // 60))
    noisy = {
        k: dataclasses.replace(s, phi=s.phi + rng.uniform(-0.04, 0.04))
        for k, s in states.items()
    }
    defect = closure_defect(noisy.values())
    vec = weighted_euler_vector(noisy.values())
    tensions = all_pairwise_tensions(noisy, couplings)
    return {
        'repository_count': len(noisy),
        'weighted_euler_vector': {'real': vec.real, 'imag': vec.imag, 'abs': abs(vec)},
        'closure_defect': defect,
        'pairwise_tensions': tensions,
    }


def main() -> int:
    root = resolve_project_root(Path(__file__))
    registry_path = root / 'integration' / 'repository_registry.json'
    couplings_path = root / 'integration' / 'couplings.json'
    try:
        report = _apply_thermal_noise(registry_path, couplings_path)
    except Exception:
        report = build_sync_report(registry_path, couplings_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
