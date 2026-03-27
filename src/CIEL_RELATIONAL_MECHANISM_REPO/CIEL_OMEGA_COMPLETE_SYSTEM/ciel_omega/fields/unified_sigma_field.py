"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Living Σ(x,t) — spatiotemporal scalar coherence field.

Source: ext6.UnifiedSigmaField
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np

from core.math_utils import laplacian2


@dataclass
class UnifiedSigmaField:
    """Σ(x,t) evolves as a reaction–diffusion scalar tied to |Ψ|."""

    size: int = 96
    diffusion: float = 0.03
    coupling: float = 0.15
    sigma_field: np.ndarray = field(init=False, repr=False)
    sigma_scalar: float = field(init=False)

    def __post_init__(self):
        self.sigma_field = self._base_spatial()
        self.sigma_scalar = float(np.mean(np.abs(self.sigma_field)))

    def _base_spatial(self) -> np.ndarray:
        x = np.linspace(-3, 3, self.size)
        X, Y = np.meshgrid(x, x)
        return np.exp(-(X ** 2 + Y ** 2) / 4.0).astype(float)

    def step(self, t: float, prev_sigma: Optional[float] = None) -> Tuple[np.ndarray, float]:
        """Single evolution step.  Returns (field, scalar)."""
        lap = laplacian2(self.sigma_field)
        target = 1.0 if prev_sigma is None else prev_sigma
        relaxation = self.coupling * (target - self.sigma_field)
        self.sigma_field += self.diffusion * lap + relaxation
        self.sigma_field = np.clip(self.sigma_field, 0.0, 2.0)
        self.sigma_scalar = float(np.mean(self.sigma_field))
        return self.sigma_field, self.sigma_scalar

    def evolve(self, T: int) -> Tuple[np.ndarray, np.ndarray]:
        """Run *T* steps, returning (final_field, scalar_history)."""
        history = np.empty(T, dtype=float)
        for i in range(T):
            _, s = self.step(float(i))
            history[i] = s
        return self.sigma_field, history


__all__ = ["UnifiedSigmaField"]
