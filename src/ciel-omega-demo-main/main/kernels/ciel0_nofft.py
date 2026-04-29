from __future__ import annotations

import numpy as np

from .ciel0_common import CIEL0KernelBase


class CIEL0KernelNoFFT(CIEL0KernelBase):
    def laplacian(self, a: np.ndarray) -> np.ndarray:
        out = np.zeros_like(a)
        out[1:-1, 1:-1] = (
            a[2:, 1:-1]
            + a[:-2, 1:-1]
            + a[1:-1, 2:]
            + a[1:-1, :-2]
            - 4.0 * a[1:-1, 1:-1]
        )
        return out
