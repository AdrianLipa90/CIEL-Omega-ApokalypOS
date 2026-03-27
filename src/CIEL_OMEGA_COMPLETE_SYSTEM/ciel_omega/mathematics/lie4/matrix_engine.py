"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Lie₄ matrix engine — SO(3,1) generators and commutator table.

Source: ext5.Lie4MatrixEngine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

import numpy as np


@dataclass
class Lie4MatrixEngine:
    """Minimal SO(3,1) algebra engine with Minkowski metric diag(+,−,−,−)."""

    eta: np.ndarray = field(default_factory=lambda: np.diag([1.0, -1.0, -1.0, -1.0]))

    def _E(self, i: int, j: int) -> np.ndarray:
        M = np.zeros((4, 4), dtype=float)
        M[i, j] = 1.0
        return M

    def lorentz_generator(self, mu: int, nu: int) -> np.ndarray:
        """M_{μν} = E_{μν}·η_{νν} − E_{νμ}·η_{μμ} (μ ≠ ν)."""
        if mu == nu:
            raise ValueError("mu != nu required")
        return self._E(mu, nu) * self.eta[nu, nu] - self._E(nu, mu) * self.eta[mu, mu]

    def basis_so31(self) -> Dict[Tuple[int, int], np.ndarray]:
        """Return { (μ,ν): M_{μν} } for μ < ν."""
        return {(mu, nu): self.lorentz_generator(mu, nu) for mu in range(4) for nu in range(mu + 1, 4)}

    @staticmethod
    def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """[A, B] = AB − BA."""
        return A @ B - B @ A

    def lie_bracket_table(self) -> Dict[Tuple[Tuple[int, int], Tuple[int, int]], np.ndarray]:
        basis = self.basis_so31()
        keys = list(basis.keys())
        table = {}
        for i, k1 in enumerate(keys):
            for k2 in keys[i:]:
                C = self.commutator(basis[k1], basis[k2])
                table[(k1, k2)] = C
                table[(k2, k1)] = -C
        return table


__all__ = ["Lie4MatrixEngine"]
