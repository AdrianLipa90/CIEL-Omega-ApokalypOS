"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Schumann resonance clock — biological rhythm reference (7.83 Hz).

Sources (unified — eliminates 3 duplicates): ext17, ext18, ext20
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


def schumann_harmonics(base: float = 7.83, k: int = 1) -> float:
    """Return the *k*-th Schumann harmonic frequency (Hz)."""
    return base * (2 * k - 1)


@dataclass
class SchumannClock:
    """Free-running phase clock locked to the first Schumann harmonic."""

    base_freq: float = 7.83
    _t0: float = 0.0

    def __post_init__(self):
        self._t0 = time.monotonic()

    def phase(self, k: int = 1, at: Optional[float] = None) -> float:
        """Current phase angle (radians) of the *k*-th harmonic."""
        t = at if at is not None else (time.monotonic() - self._t0)
        return 2.0 * np.pi * schumann_harmonics(self.base_freq, k) * t

    def carrier(self, shape: Tuple[int, int], amp: float = 1.0, k: int = 1) -> np.ndarray:
        """Return a 2-D carrier wave at the current clock phase."""
        ph = self.phase(k=k)
        return amp * np.cos(ph) * np.ones(shape, dtype=float)


__all__ = ["schumann_harmonics", "SchumannClock"]
