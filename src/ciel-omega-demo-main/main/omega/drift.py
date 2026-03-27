from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .field_ops import field_norm, normalize_field
from .schumann import SchumannClock


@dataclass
class OmegaDriftCore:
    clock: SchumannClock
    drift_gain: float = 0.05
    harmonic: int = 1
    renorm: bool = True

    def step(self, psi: np.ndarray, sigma_scalar: float = 1.0) -> np.ndarray:
        carrier = self.clock.carrier(psi.shape, amp=1.0, k=self.harmonic)
        psi_next = psi * np.exp(1j * self.drift_gain * float(sigma_scalar)) * carrier
        if self.renorm:
            psi_next = normalize_field(psi_next)
        return psi_next
