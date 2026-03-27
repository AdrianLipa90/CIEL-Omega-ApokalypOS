"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Introspection — lightweight ego↔world correlation check (stateless).

Source: ext19.Introspection
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import numpy as np


@dataclass
class Introspection:
    """Simple correlation-based integration/dissociation probe."""

    low_thr: float = 0.3
    high_thr: float = 0.8

    def state(self, ego: np.ndarray, world: np.ndarray) -> Dict[str, Any]:
        a = ego.real.ravel()
        b = world.real.ravel()
        a = (a - a.mean()) / (a.std() + 1e-12)
        b = (b - b.mean()) / (b.std() + 1e-12)
        rho = float(np.dot(a, b) / (len(a) - 1))
        st = (
            "integration" if rho > self.high_thr
            else "dissociation" if rho < self.low_thr
            else "mixed"
        )
        return {"rho": rho, "state": st}


__all__ = ["Introspection"]
