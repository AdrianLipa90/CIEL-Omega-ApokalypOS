"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Backend adapter — bridge to external simulation backends with CSF2 fallback.

Source: ext20.BackendAdapter
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

import numpy as np

from ciel_omega.core.math_utils import field_norm
from ciel_omega.core.physics.csf_simulator import CSF2Kernel, CSF2State


class BackendAdapter:
    """Wraps an external backend (set_fields/step/get_fields) or falls back to CSF2."""

    def __init__(self, backend: Optional[Any] = None, grid_size: int = 96):
        self._fallback_kernel = CSF2Kernel(dt=0.02)
        self._fallback_state: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self.backend = backend
        self.grid_size = grid_size

        if self.backend is None:
            x = np.linspace(-2, 2, grid_size)
            X, Y = np.meshgrid(x, x)
            psi = np.exp(-(X ** 2 + Y ** 2)) * np.exp(1j * (X + 0.2 * Y))
            psi /= field_norm(psi)
            sigma = np.exp(-(X ** 2 + Y ** 2) / 2.0)
            self._fallback_state = (psi.astype(np.complex128), sigma.astype(np.float64))

    def set_fields(self, psi: np.ndarray, sigma: np.ndarray) -> None:
        if self.backend is not None and hasattr(self.backend, "set_fields"):
            self.backend.set_fields(psi, sigma)
        else:
            self._fallback_state = (psi.copy(), sigma.copy())

    def step(self, dt: float) -> None:
        if self.backend is not None and hasattr(self.backend, "step"):
            self.backend.step(dt=dt)
        elif self._fallback_state is not None:
            psi, sigma = self._fallback_state
            s = CSF2State(psi, sigma, np.ones_like(psi) * 0.1, np.zeros_like(sigma))
            self._fallback_kernel.dt = dt
            s2 = self._fallback_kernel.step(s)
            self._fallback_state = (s2.psi, s2.sigma)

    def get_fields(self) -> Tuple[np.ndarray, np.ndarray]:
        if self.backend is not None and hasattr(self.backend, "get_fields"):
            return self.backend.get_fields()
        assert self._fallback_state is not None
        return self._fallback_state


__all__ = ["BackendAdapter"]
