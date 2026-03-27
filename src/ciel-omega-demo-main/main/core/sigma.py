from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .compute_backend import ComputeBackend, ComputeMode


@dataclass
class SoulInvariantOperator:
    eps: float = 1e-12
    mode: ComputeMode = 'fft'

    def compute_sigma_invariant(self, field: np.ndarray) -> float:
        backend = ComputeBackend(mode=self.mode)
        return backend.sigma_invariant(field, eps=self.eps)

    def rescale_to_ethics_bound(self, field: np.ndarray, bound: float = 0.90) -> np.ndarray:
        amp = np.sqrt(np.mean(np.abs(field) ** 2)) + self.eps
        target = np.sqrt(bound)
        return field * (target / amp)
