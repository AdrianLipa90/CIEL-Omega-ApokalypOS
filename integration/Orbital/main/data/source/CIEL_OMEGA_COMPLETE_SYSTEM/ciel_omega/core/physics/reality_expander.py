"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Non-linear field expansion (no-FFT, vectorised).

Source: ext6.RealityExpander
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ciel_omega.core.math_utils import laplacian2, field_norm


@dataclass
class RealityExpander:
    """Non-linear growth of a seed field via reaction–diffusion."""

    diffusion: float = 0.02
    reaction: float = 0.1
    steps: int = 50

    def expand(self, seed_field: np.ndarray) -> np.ndarray:
        """Evolve *seed_field* through reaction–diffusion dynamics."""
        psi = seed_field.astype(complex).copy()
        for _ in range(self.steps):
            lap = laplacian2(psi)
            psi += self.diffusion * lap + self.reaction * psi * (1.0 - np.abs(psi))
            psi /= field_norm(psi)
        return psi


__all__ = ["RealityExpander"]
