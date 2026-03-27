"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Automatic backend selection: CuPy (GPU) → Numba JIT (CPU) → pure NumPy.

Source: ext1.GPUEngine
"""

from __future__ import annotations

import numpy as np


class GPUEngine:
    """Transparent compute backend for heavy field operations."""

    def __init__(self, enable_gpu: bool = True, enable_numba: bool = True):
        self._cupy = None
        if enable_gpu:
            try:
                import cupy as cp  # type: ignore
                self._cupy = cp
            except Exception:
                pass

        self._numba_njit = None
        if enable_numba:
            try:
                from numba import njit  # type: ignore
                self._numba_njit = njit
            except Exception:
                pass

        self._laplacian_cpu = self._build_laplacian_cpu()

    # -- array movement -----------------------------------------------------

    def xp(self):
        """Return the active array module (cupy or numpy)."""
        return self._cupy if self._cupy is not None else np

    def to_xp(self, arr: np.ndarray):
        if self._cupy is None:
            return arr
        return self._cupy.asarray(arr)

    def to_np(self, arr):
        if self._cupy is None:
            return arr
        return self._cupy.asnumpy(arr)

    # -- field operations ---------------------------------------------------

    def gradient2(self, field):
        """Central-difference gradient (dy, dx) on the active backend."""
        xp = self.xp()
        gx = xp.zeros_like(field)
        gy = xp.zeros_like(field)
        gx[:, 1:-1] = 0.5 * (field[:, 2:] - field[:, :-2])
        gy[1:-1, :] = 0.5 * (field[2:, :] - field[:-2, :])
        return gy, gx

    def laplacian(self, field):
        """5-point Laplacian — GPU or JIT-compiled CPU."""
        if self._cupy is not None:
            xp = self._cupy
            out = xp.zeros_like(field)
            out[1:-1, 1:-1] = (
                field[2:, 1:-1] + field[:-2, 1:-1]
                + field[1:-1, 2:] + field[1:-1, :-2]
                - 4.0 * field[1:-1, 1:-1]
            )
            return out
        return self._laplacian_cpu(field)

    def _build_laplacian_cpu(self):
        def lap_cpu(a: np.ndarray) -> np.ndarray:
            out = np.zeros_like(a)
            out[1:-1, 1:-1] = (
                a[2:, 1:-1] + a[:-2, 1:-1]
                + a[1:-1, 2:] + a[1:-1, :-2]
                - 4.0 * a[1:-1, 1:-1]
            )
            return out

        if self._numba_njit is not None:
            return self._numba_njit(cache=True, fastmath=True)(lap_cpu)
        return lap_cpu


__all__ = ["GPUEngine"]
