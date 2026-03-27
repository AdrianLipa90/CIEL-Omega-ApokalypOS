"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Soul Invariant Σ — spectral coherence measure of consciousness fields.

Two implementations (both available):
  - SoulInvariant         — gradient-based (no-FFT, lighter)  [ext3]
  - SoulInvariantOperator — FFT-based (spectral, richer)      [ext1]
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SoulInvariant:
    """Gradient-based Σ — log-weighted gradient energy measure.

    Lightweight, no-FFT. Good for real-time loops.
    """

    delta: float = 0.3
    eps: float = 1e-12

    def compute(self, field: np.ndarray) -> float:
        """Σ = log(1 + ⟨|∇f|²⟩ / ⟨|f|²⟩)"""
        f = np.abs(field)
        norm = float(np.mean(f ** 2))
        grad_energy = float(np.mean(sum(np.abs(k) ** 2 for k in np.gradient(f))))
        return float(np.log1p(grad_energy / (norm + self.eps)))

    def normalise(self, field: np.ndarray) -> np.ndarray:
        """Rescale field so that Σ → 1 normalisation."""
        sigma = self.compute(field)
        return field / (np.sqrt(sigma) + self.eps)


@dataclass
class SoulInvariantOperator:
    """FFT-based Σ — spectral power weighted by log(1 + |k|²).

    Richer spectral information; requires FFT.
    """

    eps: float = 1e-12

    def compute_sigma_invariant(self, field: np.ndarray) -> float:
        F = np.fft.fft2(field)
        power = np.abs(F) ** 2
        h, w = field.shape
        ky = np.fft.fftfreq(h)
        kx = np.fft.fftfreq(w)
        k2 = ky[:, None] ** 2 + kx[None, :] ** 2
        return float(np.mean(power * np.log1p(k2 + self.eps)))

    def rescale_to_ethics_bound(self, field: np.ndarray, bound: float = 0.90) -> np.ndarray:
        amp = np.sqrt(np.mean(np.abs(field) ** 2)) + self.eps
        target = np.sqrt(bound)
        return field * (target / amp)


__all__ = ["SoulInvariant", "SoulInvariantOperator"]
