"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Collatz ↔ LIE₄ bridge — experimental invariants.

Source: ext18.ColatzLie4Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class ColatzLie4Engine:
    """Map Collatz sequences to SO(3,1) group products for invariant extraction."""

    steps: int = 64

    def collatz_seq(self, n: int) -> List[int]:
        assert n > 0
        seq = [n]
        while n != 1 and len(seq) < self.steps:
            n = (3 * n + 1) if (n % 2) else (n // 2)
            seq.append(n)
        return seq

    def _E(self, i: int, j: int) -> np.ndarray:
        M = np.zeros((4, 4)); M[i, j] = 1.0; return M

    def lorentz_gen(self, mu: int, nu: int) -> np.ndarray:
        eta = np.diag([1.0, -1.0, -1.0, -1.0])
        return self._E(mu, nu) * eta[nu, nu] - self._E(nu, mu) * eta[mu, mu]

    def invariant(self, n: int) -> Dict[str, float]:
        seq = self.collatz_seq(n)
        G = np.eye(4)
        for k, val in enumerate(seq[:8]):
            i = (val % 3) + 1
            A = self.lorentz_gen(0, i)
            G = G @ (np.eye(4) + (0.05 + 0.01 * k) * A)
        return {
            "det": float(np.linalg.det(G)),
            "trace": float(np.trace(G)),
            "spec": float(np.max(np.real(np.linalg.eigvals(G)))),
            "len": len(seq),
        }


__all__ = ["ColatzLie4Engine"]
