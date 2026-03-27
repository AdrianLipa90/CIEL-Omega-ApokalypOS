"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Memory synchroniser — blend Σ field with memory trace.

Source: ext19.MemorySynchronizer
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class MemorySynchronizer:
    """Synchronise Σ scalar field with a running memory trace (Ψ)."""

    alpha: float = 0.1

    def update(self, sigma: np.ndarray, psi: np.ndarray) -> np.ndarray:
        """Return updated Σ blended toward |Ψ|."""
        return (1 - self.alpha) * sigma + self.alpha * np.abs(psi)


__all__ = ["MemorySynchronizer"]
