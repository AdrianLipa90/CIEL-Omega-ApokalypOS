"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

All paradox operators (no-FFT, vectorised).

Sources:
  - ext2: IdentityDriftParadox, TemporalEchoParadox, InformationMirrorParadox
  - ext5: ParadoxFilters (twin_identity, echo, boundary_collapse)
  - ext19: ParadoxStress
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ciel_omega.core.math_utils import field_norm


# ---------------------------------------------------------------------------
# ext2 paradoxes — stateful resolvers
# ---------------------------------------------------------------------------

class IdentityDriftParadox:
    """Drift resolution: blend Ψ toward S proportional to distance."""

    def resolve(self, psi: np.ndarray, S: np.ndarray) -> np.ndarray:
        delta = np.mean(np.abs(psi - S))
        w = 1.0 - np.exp(-delta)
        return (1.0 - w) * psi + w * S


class TemporalEchoParadox:
    """Momentum echo: curr′ = curr + α(curr − prev)."""

    def resolve(self, prev: np.ndarray, curr: np.ndarray, alpha: float = 0.1) -> np.ndarray:
        return curr + alpha * (curr - prev)


class InformationMirrorParadox:
    """Phase-contrast boost without FFT (local gradient sharpening)."""

    def resolve(self, psi: np.ndarray, beta: float = 0.05) -> np.ndarray:
        gx = np.zeros_like(psi); gy = np.zeros_like(psi)
        gx[:, 1:-1] = psi[:, 2:] - psi[:, :-2]
        gy[1:-1, :] = psi[2:, :] - psi[:-2, :]
        sharp = np.sqrt(np.abs(gx) ** 2 + np.abs(gy) ** 2)
        boost = 1 + beta * (sharp / (np.max(sharp) + 1e-12))
        out = psi * boost
        out /= field_norm(out)
        return out


# ---------------------------------------------------------------------------
# ext5 paradox filters — static methods
# ---------------------------------------------------------------------------

class ParadoxFilters:
    """Lightweight paradox-stabilisation filters (no-FFT)."""

    @staticmethod
    def twin_identity(psi: np.ndarray) -> np.ndarray:
        """Twin symmetry (real/imag) — preserves amplitude."""
        conj = np.conjugate(psi)
        return 0.5 * (psi + conj) + 0.5j * (psi - conj)

    @staticmethod
    def echo(prev: np.ndarray, curr: np.ndarray, k: float = 0.08) -> np.ndarray:
        return curr + k * (curr - prev)

    @staticmethod
    def boundary_collapse(psi: np.ndarray, tol: float = 1e-3) -> np.ndarray:
        """Squeeze boundary values toward mean to prevent edge divergence."""
        out = psi.copy()
        m = np.mean(psi)
        out[0, :] = (1 - tol) * out[0, :] + tol * m
        out[-1, :] = (1 - tol) * out[-1, :] + tol * m
        out[:, 0] = (1 - tol) * out[:, 0] + tol * m
        out[:, -1] = (1 - tol) * out[:, -1] + tol * m
        return out


# ---------------------------------------------------------------------------
# ext19 paradox stress — controlled semantic jitter
# ---------------------------------------------------------------------------

@dataclass
class ParadoxStress:
    """Apply controlled noise to a CSF2-like state for stress testing."""

    strength: float = 0.1

    def apply_to_field(self, psi: np.ndarray) -> np.ndarray:
        jitter = (np.random.rand(*psi.shape) - 0.5) * self.strength
        return psi + jitter


__all__ = [
    "IdentityDriftParadox",
    "TemporalEchoParadox",
    "InformationMirrorParadox",
    "ParadoxFilters",
    "ParadoxStress",
]
