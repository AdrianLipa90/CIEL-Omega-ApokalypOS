"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Consciousness Field (CSF) simulators — real-space evolution (no-FFT).

Sources:
  - ext2.CSFSimulator      — Ψ(x,t) field evolution (smooth + gradient drift)
  - ext19.CSF2State/Kernel — 4-field state (Ψ, Σ, Λ, Ω) with Laplacian dynamics
  - ext2.CIELFullKernelLite — orchestrator integrating CSF + paradoxes + RCDE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ciel_omega.core.math_utils import laplacian2, field_norm, smooth2d


# ---------------------------------------------------------------------------
# CSF Simulator — basic Ψ(x,t) evolution
# ---------------------------------------------------------------------------

@dataclass
class CSFSimulator:
    """Real-space consciousness field Ψ(x,t) with gradient-drift evolution."""

    size: int = 128
    sigma: float = 2.0
    dt: float = 0.01
    smooth_strength: float = 0.15
    seed: Optional[int] = None

    X: np.ndarray = field(init=False, repr=False)
    Y: np.ndarray = field(init=False, repr=False)
    psi: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        if self.seed is not None:
            np.random.seed(self.seed)
        x = np.linspace(-3.0, 3.0, self.size)
        y = np.linspace(-3.0, 3.0, self.size)
        self.X, self.Y = np.meshgrid(x, y)
        env = np.exp(-(self.X ** 2 + self.Y ** 2) / (self.sigma ** 2))
        phase = np.exp(1j * (self.X + self.Y))
        self.psi = env * phase

    def step(self, n: int = 1, drift: float = 1.0) -> None:
        """Iterative evolution in real domain."""
        for _ in range(n):
            gy = np.zeros_like(self.psi)
            gx = np.zeros_like(self.psi)
            gy[1:-1, :] = 0.5 * (self.psi[2:, :] - self.psi[:-2, :])
            gx[:, 1:-1] = 0.5 * (self.psi[:, 2:] - self.psi[:, :-2])
            self.psi += 1j * self.dt * drift * (gy + gx)

            s_real = smooth2d(self.psi.real)
            s_imag = smooth2d(self.psi.imag)
            self.psi = (1 - self.smooth_strength) * self.psi + self.smooth_strength * (
                s_real + 1j * s_imag
            )
            self.psi /= field_norm(self.psi)


# ---------------------------------------------------------------------------
# CSF2 — 4-field state (Ψ, Σ, Λ, Ω)
# ---------------------------------------------------------------------------

@dataclass
class CSF2State:
    """Extended consciousness-field state with four coupled fields."""

    psi: np.ndarray       # consciousness field Ψ
    sigma: np.ndarray     # coherence field Σ
    lam: np.ndarray       # Λ₀ protection field
    omega: np.ndarray     # Ω drift-phase field

    def clone(self) -> "CSF2State":
        return CSF2State(
            psi=self.psi.copy(),
            sigma=self.sigma.copy(),
            lam=self.lam.copy(),
            omega=self.omega.copy(),
        )


@dataclass
class CSF2Kernel:
    """Local Laplacian dynamics for the 4-field CSF2 state."""

    dt: float = 0.01
    diffusion: float = 0.05

    def step(self, s: CSF2State) -> CSF2State:
        """Single evolution step (Laplacian diffusion + non-linear coupling)."""
        lap_psi = laplacian2(s.psi)
        lap_sigma = laplacian2(s.sigma)

        new_psi = s.psi + self.dt * (
            self.diffusion * lap_psi + 0.1j * s.sigma * s.psi
        )
        # normalise Ψ
        new_psi /= field_norm(new_psi)

        new_sigma = s.sigma + self.dt * (
            0.5 * self.diffusion * lap_sigma
            - 0.05 * (s.sigma - np.abs(new_psi))
        )

        new_lam = s.lam * np.exp(-0.01 * self.dt)
        new_omega = s.omega + self.dt * 0.02 * np.angle(new_psi)

        return CSF2State(psi=new_psi, sigma=new_sigma, lam=new_lam, omega=new_omega)


def make_csf2_seed(n: int = 96) -> CSF2State:
    """Create a default initial CSF2 state for testing."""
    x = np.linspace(-3, 3, n)
    X, Y = np.meshgrid(x, x)
    psi = np.exp(-(X ** 2 + Y ** 2) / 2) * np.exp(1j * X)
    sigma = np.abs(psi)
    lam = np.ones_like(sigma)
    omega = np.zeros_like(sigma)
    return CSF2State(psi=psi, sigma=sigma, lam=lam, omega=omega)


__all__ = [
    "CSFSimulator",
    "CSF2State",
    "CSF2Kernel",
    "make_csf2_seed",
]
