from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


ComputeMode = Literal['fft', 'nofft']


@dataclass(frozen=True)
class ComputeBackend:
    mode: ComputeMode = 'fft'

    def sigma_invariant(self, field: np.ndarray, *, eps: float = 1e-12) -> float:
        if self.mode == 'fft':
            F = np.fft.fft2(field)
            power = np.abs(F) ** 2
            h, w = field.shape
            ky = np.fft.fftfreq(h)
            kx = np.fft.fftfreq(w)
            k2 = (ky[:, None] ** 2) + (kx[None, :] ** 2)
            return float(np.mean(power * np.log1p(k2 + eps)))

        gy, gx = np.gradient(field)
        energy = (np.abs(gx) ** 2) + (np.abs(gy) ** 2)
        return float(np.mean(np.log1p(energy + eps)))
