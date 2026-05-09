"""HTRI vectorized phase networks.

This module upgrades the local HTRI model from scalar Kuramoto-style updates
into a dense matrix formulation with explicit potential, field, and spectral
observables. The implementation is intentionally classical: dense phase-space
math, not quantum dynamics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np



def plo_frequencies(n: int, f_base: float = 1.0, target_beat_hz: float = 7.83) -> np.ndarray:
    """Frequency ladder for phase oscillators.

    The target beat is reported for diagnostics only. The construction is a
    classical dense phase profile: no quantum claim, just structured spectrum.
    """
    spread = 28.0 * (n / 14080.0)
    return np.array([f_base + (i / max(n, 1)) * spread for i in range(n)], dtype=np.float64)

ArrayLike = np.ndarray
Topology = Literal["all_to_all", "ring", "grid_2d"]


def build_all_to_all_matrix(n: int, kappa: float) -> np.ndarray:
    mat = np.full((n, n), float(kappa), dtype=np.float64)
    np.fill_diagonal(mat, 0.0)
    return mat


def build_ring_matrix(n: int, kappa: float, nearest: int = 1, decay: float = 1.0) -> np.ndarray:
    idx = np.arange(n)
    dist = np.abs(idx[:, None] - idx[None, :])
    circular = np.minimum(dist, n - dist)
    mat = np.zeros((n, n), dtype=np.float64)
    mask = (circular > 0) & (circular <= nearest)
    mat[mask] = kappa / np.power(circular[mask], decay)
    return mat


def build_grid_matrix(width: int, height: int, kappa: float) -> np.ndarray:
    n = width * height
    coords = np.stack(np.unravel_index(np.arange(n), (height, width)), axis=1).astype(np.float64)
    diff = coords[:, None, :] - coords[None, :, :]
    dist = np.sqrt(np.sum(diff * diff, axis=-1))
    mat = np.zeros((n, n), dtype=np.float64)
    mask = dist > 0
    mat[mask] = kappa / dist[mask]
    return mat


@dataclass
class DensePhaseNetwork:
    """Dense vectorized phase network with matrix coupling."""

    n: int
    dt: float = 1e-3
    kappa: float = 0.1
    topology: Topology = "all_to_all"
    field_strength: float = 0.0
    field_phase: ArrayLike | None = None
    matrix: ArrayLike | None = None
    ring_nearest: int = 1
    ring_decay: float = 1.0
    grid_shape: tuple[int, int] | None = None

    phases: ArrayLike = field(init=False)
    omegas: ArrayLike = field(init=False)
    sigma: ArrayLike = field(init=False)
    coherence: float = field(init=False, default=0.0)
    potential: float = field(init=False, default=0.0)
    t: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        self.phases = np.zeros(self.n, dtype=np.float64)
        self.omegas = plo_frequencies(self.n).astype(np.float64)
        self.sigma = np.zeros(self.n, dtype=np.float64)
        self.field_phase = np.zeros(self.n, dtype=np.float64) if self.field_phase is None else np.asarray(self.field_phase, dtype=np.float64)
        if self.field_phase.shape != (self.n,):
            raise ValueError(f"field_phase must have shape ({self.n},)")
        self.matrix = self._build_matrix() if self.matrix is None else np.asarray(self.matrix, dtype=np.float64)
        if self.matrix.shape != (self.n, self.n):
            raise ValueError(f"coupling matrix must have shape ({self.n}, {self.n})")
        np.fill_diagonal(self.matrix, 0.0)
        # Keep symmetric kernel for scalar potential by default.
        self.matrix = 0.5 * (self.matrix + self.matrix.T)

    def _build_matrix(self) -> np.ndarray:
        if self.topology == "all_to_all":
            return build_all_to_all_matrix(self.n, self.kappa)
        if self.topology == "ring":
            return build_ring_matrix(self.n, self.kappa, self.ring_nearest, self.ring_decay)
        if self.topology == "grid_2d":
            if self.grid_shape is None:
                raise ValueError("grid_shape is required for grid_2d topology")
            width, height = self.grid_shape
            if width * height != self.n:
                raise ValueError("grid_shape does not match n")
            return build_grid_matrix(width, height, self.kappa)
        raise ValueError(f"unsupported topology: {self.topology}")

    @property
    def phase_differences(self) -> np.ndarray:
        return self.phases[:, None] - self.phases[None, :]

    @property
    def phase_kernel(self) -> np.ndarray:
        return np.exp(1j * self.phase_differences)

    def coupling_field(self) -> np.ndarray:
        diff = self.phase_differences
        return np.sum(self.matrix * np.sin(diff), axis=1) / max(self.n, 1)

    def external_field(self) -> np.ndarray:
        if self.field_strength == 0.0:
            return np.zeros(self.n, dtype=np.float64)
        return self.field_strength * np.sin(self.field_phase - self.phases)

    def potential_matrix(self) -> np.ndarray:
        diff = self.phase_differences
        return self.matrix * (1.0 - np.cos(diff))

    def potential_energy(self) -> float:
        return float(0.5 * np.sum(self.potential_matrix()) / max(self.n, 1))

    def order_parameter(self) -> float:
        """Kuramoto R = |mean(e^iφ)| with Heisenberg soft clip.

        R=1.0 is a frozen singularity — full coherence blocks evolution.
        Clip: R_max = 1 - dt*std(omegas), emergent from network geometry.
        """
        r = float(np.abs(np.mean(np.exp(1j * self.phases))))
        epsilon_H = self.dt * float(np.std(self.omegas))
        return min(r, 1.0 - max(epsilon_H, 1e-9))

    def laplacian(self) -> np.ndarray:
        degree = np.sum(self.matrix, axis=1)
        return np.diag(degree) - self.matrix

    def spectral_radius(self, iterations: int = 12) -> float:
        """Fast spectral-radius estimate using power iteration.

        A full eigen decomposition is overkill for the diagnostics path and can
        dominate runtime on the 768-oscillator case. The power method keeps the
        observable informative while remaining lightweight.
        """
        A = np.abs(self.laplacian())
        v = np.ones(self.n, dtype=np.float64)
        v /= max(np.linalg.norm(v), 1e-12)
        for _ in range(max(1, int(iterations))):
            v = A @ v
            norm = np.linalg.norm(v)
            if norm < 1e-12:
                return 0.0
            v /= norm
        return float(np.linalg.norm(A @ v))

    def step(self) -> None:
        prev = self.phases.copy()
        coupling = self.coupling_field()
        field = self.external_field()
        self.phases = (self.phases + self.dt * (self.omegas + coupling + field)) % (2.0 * np.pi)
        delta = np.arctan2(np.sin(self.phases - prev), np.cos(self.phases - prev))
        self.sigma += delta / (2.0 * np.pi)
        self.t += self.dt
        self.coherence = self.order_parameter()
        self.potential = self.potential_energy()

    def run(self, steps: int) -> dict[str, Any]:
        for _ in range(int(steps)):
            self.step()
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        return {
            "n_oscillators": self.n,
            "coherence": round(self.coherence, 6),
            "potential": round(self.potential, 6),
            "soul_invariant": round(float(np.mean(self.sigma)), 6),
            "sigma_max": round(float(np.max(np.abs(self.sigma))), 6),
            "spectral_radius": round(self.spectral_radius(), 6),
            "field_norm": round(float(np.linalg.norm(self.external_field())), 6),
            "t": round(self.t, 6),
        }
