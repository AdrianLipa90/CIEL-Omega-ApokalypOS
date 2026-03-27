"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Unsupervised prediction via exponentially-weighted history.

Source: ext10.PredictiveCore
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class PredictiveCore:
    """predict(history) = Σ exp(−t/τ) · x_t / Σ exp(−t/τ)."""

    tau: float = 12.0

    def predict(self, history: List[float]) -> float:
        if not history:
            return 0.0
        h = np.asarray(history, dtype=float)
        t = np.arange(len(h))[::-1]
        w = np.exp(-t / max(self.tau, 1e-6))
        return float(np.sum(w * h) / (np.sum(w) + 1e-12))


__all__ = ["PredictiveCore"]
