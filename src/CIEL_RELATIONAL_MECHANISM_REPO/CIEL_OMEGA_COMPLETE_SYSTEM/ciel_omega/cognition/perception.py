"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Perceptive layer: Percept(x,y) = Σ(x,y) · (Re(Ψ) + |Im(Ψ)|).

Source: ext10.PerceptiveLayer
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class PerceptiveLayer:
    """Sensory map combining consciousness field Ψ with coherence Σ."""

    clip_percentile: Optional[float] = 99.5

    def compute(self, psi_field: np.ndarray, sigma_field: np.ndarray) -> np.ndarray:
        psi = psi_field.astype(np.complex128, copy=False)
        sig = sigma_field.astype(np.float64, copy=False)
        percept = sig * (psi.real + np.abs(psi.imag))
        if self.clip_percentile is not None:
            hi = np.percentile(percept, self.clip_percentile)
            percept = np.clip(percept, 0.0, hi) / (hi + 1e-12)
        else:
            percept = percept / (np.max(percept) + 1e-12)
        return percept


__all__ = ["PerceptiveLayer"]
