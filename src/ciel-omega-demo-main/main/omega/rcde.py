from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .field_ops import field_norm


@dataclass
class RCDECalibrator:
    lam: float = 0.2
    dt: float = 0.05
    sigma: float = 0.5

    def step(self, psi: np.ndarray) -> float:
        energy = field_norm(psi) ** 2
        self.sigma = float(self.sigma + self.dt * self.lam * (energy - self.sigma))
        self.sigma = float(np.clip(self.sigma, 0.0, 1.5))
        return self.sigma
