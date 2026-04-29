"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Gradient-based optimiser for reality constants.

Source: ext2.QuantumOptimiser
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Tuple


@dataclass
class QuantumOptimiser:
    """Numerically optimise constants via finite-difference gradient descent."""

    lr: float = 0.05
    steps: int = 50
    ethical_weight: float = 1.0

    def optimize_constants(
        self,
        constants: Dict[str, float],
        metrics_fn: Callable[[Dict[str, float]], Tuple[float, float, bool]],
    ) -> Dict[str, float]:
        """Return optimised *constants* minimising (1−coh)²+(1−fid)²+penalty."""
        keys = list(constants.keys())
        eps = 1e-3
        for _ in range(self.steps):
            coh, fid, ok = metrics_fn(constants)
            loss = (1 - coh) ** 2 + (1 - fid) ** 2 + (0 if ok else 0.1 * self.ethical_weight)
            grad = {}
            for k in keys:
                orig = constants[k]
                constants[k] = orig + eps
                c2, f2, o2 = metrics_fn(constants)
                loss2 = (1 - c2) ** 2 + (1 - f2) ** 2 + (0 if o2 else 0.1 * self.ethical_weight)
                grad[k] = (loss2 - loss) / eps
                constants[k] = orig
            for k in keys:
                constants[k] -= self.lr * grad[k]
        return constants


__all__ = ["QuantumOptimiser"]
