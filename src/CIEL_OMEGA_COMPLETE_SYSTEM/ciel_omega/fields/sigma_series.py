"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Dynamic Σ(t) series — convergent evolution of the soul invariant.
Σ_{t+1} = Σ_t + α^(t+1) · (1 − Σ_t),  α ∈ (0,1]

Source: ext5.SigmaSeries
Fix: original used α^t which gives α^0=1.0 → instant jump to 1.0.
     Now uses α^(t+1) for gradual convergence.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.math_utils import field_norm


@dataclass
class SigmaSeries:
    """Time-series of Σ converging to 1.0 at rate α."""

    alpha: float = 0.618       # "golden" growth coefficient
    sigma0: float = 0.42       # initial coherence
    steps: int = 256

    def run(self) -> np.ndarray:
        """Return the full Σ(t) trajectory as a 1-D array."""
        a_pow = self.alpha ** np.arange(1, self.steps + 1, dtype=float)
        sigma = np.empty(self.steps, dtype=float)
        s = float(self.sigma0)
        for i in range(self.steps):
            s = s + a_pow[i] * (1.0 - s)
            sigma[i] = s
        return sigma

    def apply_to_field(self, field: np.ndarray) -> np.ndarray:
        """Gently rescale *field* amplitude to match the final Σ_T value."""
        sigma_T = float(self.run()[-1])
        amp = field_norm(field)
        target = np.sqrt(sigma_T)
        return field * (target / amp)


__all__ = ["SigmaSeries"]
