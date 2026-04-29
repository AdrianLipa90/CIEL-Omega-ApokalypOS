from __future__ import annotations

import numpy as np

from .ciel0_common import CIEL0KernelBase


class CIEL0KernelFFT(CIEL0KernelBase):
    def __init__(self, *, grid_size: int = 64, length: float = 10.0, **kwargs) -> None:
        super().__init__(grid_size=grid_size, **kwargs)
        self.length = float(length)
        self._k2 = self._make_k2(self.grid_size, self.length)

    def _make_k2(self, n: int, length: float) -> np.ndarray:
        dx = length / float(n)
        k = 2.0 * np.pi * np.fft.fftfreq(n, d=dx)
        kx, ky = np.meshgrid(k, k)
        return (kx**2 + ky**2).astype(float)

    def laplacian(self, a: np.ndarray) -> np.ndarray:
        A = np.fft.fft2(a)
        out = np.fft.ifft2(-self._k2 * A)
        return out
