"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

EEG signal pre-processing — band-power extraction (vectorised, no-FFT).

Source: ext7.EEGProcessor
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class EEGProcessor:
    """Extract EEG band powers via simple sliding-window variance proxy."""

    sample_rate: float = 128.0

    def band_powers(self, signal: np.ndarray) -> Dict[str, float]:
        """Return approximate band powers for δ, θ, α, β, γ.

        Uses a cheap proxy: variance of moving-average residuals at
        different window sizes (no actual FFT needed).
        """
        s = np.asarray(signal, dtype=float).ravel()
        n = len(s)
        if n < 8:
            return {b: 0.0 for b in ("delta", "theta", "alpha", "beta", "gamma")}

        def _var_at_scale(k: int) -> float:
            kernel = np.ones(k) / k
            smoothed = np.convolve(s, kernel, mode="same")
            return float(np.var(s - smoothed))

        return {
            "delta": _var_at_scale(max(1, n // 2)),
            "theta": _var_at_scale(max(1, n // 4)),
            "alpha": _var_at_scale(max(1, n // 8)),
            "beta":  _var_at_scale(max(1, n // 16)),
            "gamma": _var_at_scale(max(1, n // 32)),
        }


__all__ = ["EEGProcessor"]
