from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from .field_ops import field_norm, laplacian2, normalize_field


@dataclass
class CSF2State:
    psi: np.ndarray
    sigma: np.ndarray
    lam: np.ndarray
    omega: np.ndarray

    def clone(self) -> 'CSF2State':
        return CSF2State(self.psi.copy(), self.sigma.copy(), self.lam.copy(), self.omega.copy())


@dataclass
class CSF2Kernel:
    dt: float = 0.05
    k_psi: float = 0.8
    k_sigma: float = 0.6
    k_couple: float = 0.5
    k_world: float = 0.2

    def step(self, s: CSF2State) -> CSF2State:
        dpsi = 1j * float(self.k_psi) * laplacian2(s.psi) + float(self.k_couple) * (s.lam * s.sigma - s.omega * s.psi)
        dsig = float(self.k_sigma) * (np.abs(s.psi) ** 2 - s.sigma) - 0.1 * s.sigma**2
        dome = 0.05 * laplacian2(s.omega) - 0.02 * (s.omega - float(np.mean(s.omega)))
        dlam = 0.1 * (s.psi * np.conj(s.psi)) - 0.05 * s.lam

        psi2 = s.psi + float(self.dt) * dpsi
        psi2 = normalize_field(psi2)
        sigma2 = np.clip(s.sigma + float(self.dt) * dsig, 0.0, 2.0)
        omega2 = s.omega + float(self.dt) * dome
        lam2 = s.lam + float(self.dt) * dlam
        return CSF2State(psi2, sigma2, lam2, omega2)


@dataclass
class MemorySynchronizer:
    alpha: float = 0.92
    beta: float = 0.08
    ms: Optional[np.ndarray] = None

    def update(self, sigma: np.ndarray, psi: np.ndarray) -> np.ndarray:
        if self.ms is None:
            self.ms = sigma.copy()
        self.ms = float(self.alpha) * self.ms + float(self.beta) * np.abs(psi)
        return self.ms


@dataclass
class Introspection:
    low_thr: float = 0.3
    high_thr: float = 0.8

    def state(self, ego: np.ndarray, world: np.ndarray) -> Tuple[float, str]:
        a = ego.real.ravel()
        b = world.real.ravel()
        a = (a - float(a.mean())) / (float(a.std()) + 1e-12)
        b = (b - float(b.mean())) / (float(b.std()) + 1e-12)
        rho = float(np.dot(a, b) / max(1, (len(a) - 1)))
        st = 'integration' if rho > float(self.high_thr) else 'dissociation' if rho < float(self.low_thr) else 'mixed'
        return rho, st
