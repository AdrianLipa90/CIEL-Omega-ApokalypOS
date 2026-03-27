"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Ω-drift cores — Schumann-synchronised phase drift for consciousness fields.

Sources (unified): ext17.OmegaDriftCore, ext18.OmegaDriftCorePlus
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from ciel_omega.bio.schumann import SchumannClock
from ciel_omega.core.math_utils import field_norm


@dataclass
class OmegaDriftCore:
    """Basic Σ-aware phase drift modulated by Schumann carrier."""

    clock: SchumannClock
    drift_gain: float = 0.05
    harmonic: int = 1
    renorm: bool = True

    def step(self, psi: np.ndarray, sigma_scalar: float = 1.0) -> np.ndarray:
        carrier = self.clock.carrier(psi.shape, amp=1.0, k=self.harmonic)
        psi_next = psi * np.exp(1j * self.drift_gain * sigma_scalar) * carrier
        if self.renorm:
            psi_next /= field_norm(psi_next)
        return psi_next


@dataclass
class OmegaDriftCorePlus:
    """Extended drift with harmonic sweep, jitter, and Schumann-awareness."""

    clock: SchumannClock
    drift_gain: float = 0.045
    harmonic: int = 1
    harmonic_sweep: Tuple[int, int] = (1, 3)
    jitter: float = 0.004
    renorm: bool = True

    def step(self, psi: np.ndarray, sigma_scalar: float = 1.0, t: Optional[float] = None) -> np.ndarray:
        hmin, hmax = self.harmonic_sweep
        h = int(np.clip(round(hmin + (hmax - hmin) * np.clip(sigma_scalar, 0.0, 1.0)), hmin, hmax))
        ph = self.clock.phase(k=h, at=t) + np.random.uniform(-self.jitter, self.jitter)
        psi_next = psi * np.exp(1j * (self.drift_gain * sigma_scalar + ph))
        if self.renorm:
            psi_next /= field_norm(psi_next)
        return psi_next


__all__ = ["OmegaDriftCore", "OmegaDriftCorePlus"]
