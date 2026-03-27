"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Quantum resonance kernel — R(S, I) computation and Schrödinger evolution.

Source: ext7.QuantumResonanceKernel
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from config.constants import CIELPhysics
from core.math_utils import laplacian2, field_norm


@dataclass
class QuantumResonanceKernel:
    """Resonance R(S, I), coherence test, and Schrödinger step."""

    physics: CIELPhysics = field(default_factory=CIELPhysics)
    min_coherence: float = 0.4

    def resonance(self, S: np.ndarray, I: np.ndarray) -> float:
        """Mean resonance between symbolic (S) and intention (I) fields."""
        inner = np.conj(S) * I
        return float(np.mean(np.abs(inner)))

    def is_coherent(self, resonance: float) -> bool:
        return resonance >= self.min_coherence

    def evolve_step(
        self,
        psi: np.ndarray,
        potential: Optional[np.ndarray] = None,
        dt: float = 0.01,
    ) -> np.ndarray:
        """Single Schrödinger-like evolution step (no-FFT)."""
        lap = laplacian2(psi)
        V = potential if potential is not None else np.zeros_like(psi)
        dpsi = -1j * (-0.5 * lap + V * psi)
        psi_new = psi + dt * dpsi
        psi_new /= field_norm(psi_new)
        return psi_new

    def integrate(self, F: np.ndarray) -> np.ndarray:
        """Cumulative Simpson-like integration of a 2D field (row-wise)."""
        return np.cumsum(F, axis=-1) * (1.0 / max(F.shape[-1], 1))


__all__ = ["QuantumResonanceKernel"]
