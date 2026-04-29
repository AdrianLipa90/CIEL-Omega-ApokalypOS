from __future__ import annotations

from typing import Any, Dict

import numpy as np

from ..core.ciel_constants import CIELConstants, DEFAULT_CONSTANTS
from .ciel0_state import CIEL0State


class CIEL0KernelBase:
    def __init__(self, *, constants: CIELConstants = DEFAULT_CONSTANTS, grid_size: int = 64) -> None:
        self.constants = constants
        self.grid_size = int(grid_size)
        self.state = self._init_state(self.grid_size)

    def laplacian(self, a: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def _init_state(self, n: int) -> CIEL0State:
        I = np.zeros((n, n), dtype=np.complex128)
        tau = np.zeros((n, n), dtype=float)
        S = np.zeros((n, n), dtype=np.complex128)
        R = np.zeros((n, n), dtype=float)
        mass = np.zeros((n, n), dtype=float)
        Lambda0 = np.zeros((n, n), dtype=float)

        x = np.linspace(-5.0, 5.0, n)
        X, Y = np.meshgrid(x, x)
        r2 = X**2 + Y**2
        g = np.exp(-r2 / 2.0)
        I[:] = g * np.exp(1j * 0.1 * (X + Y))
        S[:] = g * np.exp(1j * 0.5)

        return CIEL0State(I=I, tau=tau, S=S, R=R, mass=mass, Lambda0=Lambda0)

    def _resonance(self, S: np.ndarray, I: np.ndarray) -> np.ndarray:
        num = np.abs(np.conj(S) * I) ** 2
        den = (np.abs(S) * np.abs(I) + 1e-15) ** 2
        return (num / den).real

    def _lambda0(self, B: np.ndarray, rho: np.ndarray, L_scale: float, alpha_res: np.ndarray) -> np.ndarray:
        rho_safe = np.maximum(rho, 1e-30)
        return (
            (B**2 / (self.constants.mu0 * rho_safe * self.constants.c**2))
            * (1.0 / max(L_scale**2, 1e-60))
            * alpha_res
        )

    def step(self, *, dt: float = 0.1) -> Dict[str, float]:
        I = self.state.I
        tau = self.state.tau
        S = self.state.S

        R = self._resonance(S, I)
        self.state.R[:] = R

        mu0_mass = self.constants.mp**2
        mass = np.sqrt(np.maximum(mu0_mass * (1.0 - R), 0.0))
        self.state.mass[:] = mass

        B = np.ones_like(R) * 1e-4
        rho = mass + 1e-10
        L_scale = self.constants.Lp * 1e20
        self.state.Lambda0[:] = self._lambda0(B, rho, L_scale, R)

        lap = self.laplacian(I)
        mag = np.maximum(np.abs(I), 1e-15)
        nonlin = 2.0 * self.constants.lambda_1 * (mag**2) * I
        phase = 1j * self.constants.lambda_3 * np.sin(tau - np.angle(I)) / mag * I
        I[:] = I + dt * (-lap - nonlin - phase)

        gy, gx = np.gradient(tau)
        rho2 = gx**2 + gy**2
        f = 1.0 / (2.0 * (1.0 + rho2**2))

        div_full = np.zeros_like(tau)
        div_full[1:-1, 1:-1] = (
            (
                f[2:, 1:-1] * (tau[2:, 1:-1] - tau[1:-1, 1:-1])
                - f[:-2, 1:-1] * (tau[1:-1, 1:-1] - tau[:-2, 1:-1])
            )
            + (
                f[1:-1, 2:] * (tau[1:-1, 2:] - tau[1:-1, 1:-1])
                - f[1:-1, :-2] * (tau[1:-1, 1:-1] - tau[1:-1, :-2])
            )
        )
        tau[:] = tau + dt * (div_full - self.constants.lambda_3 * np.sin(tau - np.angle(I)))

        S[:] = S + dt * 0.1 * I

        return {
            'resonance_mean': float(np.mean(self.state.R)),
            'mass_mean': float(np.mean(self.state.mass)),
            'lambda0_mean': float(np.mean(np.abs(self.state.Lambda0))),
        }

    def run(self, *, steps: int = 50, dt: float = 0.1) -> Dict[str, Any]:
        last: Dict[str, float] = {}
        for _ in range(int(steps)):
            last = self.step(dt=dt)
        return {'final': last}
