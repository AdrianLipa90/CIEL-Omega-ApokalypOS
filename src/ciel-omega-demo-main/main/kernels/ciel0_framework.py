from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

from ..core.ciel_constants import CIELConstants, DEFAULT_CONSTANTS


@dataclass
class CIEL0FrameworkState:
    I_field: np.ndarray
    tau_field: np.ndarray
    S_field: np.ndarray
    R_field: np.ndarray
    mass_field: np.ndarray
    Lambda0_field: np.ndarray


class CIEL0FrameworkKernel:
    def __init__(
        self,
        *,
        constants: CIELConstants = DEFAULT_CONSTANTS,
        grid_size: int = 64,
        compute_mode: str = 'nofft',
        length: float = 10.0,
    ) -> None:
        self.constants = constants
        self.grid_size = int(grid_size)
        self.compute_mode = str(compute_mode)
        self.length = float(length)

        self._k2: Optional[np.ndarray] = None
        if self.compute_mode == 'fft':
            self._k2 = self._make_k2(self.grid_size, self.length)

        self.state = self._init_state(self.grid_size)

    def _make_k2(self, n: int, length: float) -> np.ndarray:
        dx = length / float(n)
        k = 2.0 * np.pi * np.fft.fftfreq(n, d=dx)
        kx, ky = np.meshgrid(k, k)
        return (kx**2 + ky**2).astype(float)

    def _laplacian(self, a: np.ndarray) -> np.ndarray:
        if self.compute_mode == 'fft':
            if self._k2 is None:
                self._k2 = self._make_k2(self.grid_size, self.length)
            A = np.fft.fft2(a)
            return np.fft.ifft2(-self._k2 * A)

        out = np.zeros_like(a)
        out[1:-1, 1:-1] = (
            a[2:, 1:-1]
            + a[:-2, 1:-1]
            + a[1:-1, 2:]
            + a[1:-1, :-2]
            - 4.0 * a[1:-1, 1:-1]
        )
        return out

    def _init_state(self, n: int) -> CIEL0FrameworkState:
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

        return CIEL0FrameworkState(
            I_field=I,
            tau_field=tau,
            S_field=S,
            R_field=R,
            mass_field=mass,
            Lambda0_field=Lambda0,
        )

    def initialize_gaussian_pulse(
        self,
        *,
        center: Optional[Tuple[int, int]] = None,
        sigma: float = 1.0,
        amplitude: float = 1.0,
    ) -> None:
        n = self.grid_size
        if center is None:
            center = (n // 2, n // 2)
        i, j = center

        y_grid, x_grid = np.ogrid[:n, :n]
        gaussian = amplitude * np.exp(-((x_grid - j) ** 2 + (y_grid - i) ** 2) / (2.0 * sigma**2))

        self.state.I_field[:] = gaussian * np.exp(1j * np.angle(gaussian + 1j * gaussian))
        self.state.S_field[:] = gaussian * np.exp(1j * 0.5 * np.pi)
        self.state.tau_field[:] = gaussian * 0.1

    def compute_resonance(self, S: np.ndarray, I: np.ndarray) -> np.ndarray:
        num = np.abs(np.conj(S) * I) ** 2
        den = (np.abs(S) * np.abs(I) + 1e-15) ** 2
        return (num / den).real

    def compute_lambda0_operator(self, B_field: np.ndarray, rho: np.ndarray, *, L_scale: Optional[float] = None) -> np.ndarray:
        if L_scale is None:
            L_scale = float(self.constants.L_planck) * 1e20
        rho_safe = np.maximum(rho, 1e-30)
        alpha_res = self.compute_resonance(self.state.S_field, self.state.I_field)
        return (B_field**2 / (float(self.constants.mu_0) * rho_safe * float(self.constants.c) ** 2)) * (1.0 / max(L_scale**2, 1e-60)) * alpha_res

    def compute_symbolic_mass(self, S: np.ndarray, I: np.ndarray, *, mu_0: Optional[float] = None) -> np.ndarray:
        if mu_0 is None:
            mu_0 = float(self.constants.m_planck) ** 2
        R = self.compute_resonance(S, I)
        mass_squared = mu_0 * (1.0 - R)
        return np.sqrt(np.maximum(mass_squared, 0.0))

    def compute_symbolic_entropy(self, R: np.ndarray) -> np.ndarray:
        R_safe = np.maximum(R, 1e-15)
        return -R_safe * np.log(R_safe)

    def compute_intention_dynamics(self, I: np.ndarray, tau: np.ndarray, *, dt: float = 0.1) -> np.ndarray:
        lap = self._laplacian(I)
        mag = np.maximum(np.abs(I), 1e-15)
        nonlin = 2.0 * float(self.constants.lambda_1) * mag**2 * I
        phase = 1j * float(self.constants.lambda_3) * np.sin(tau - np.angle(I)) / mag * I
        dI = -lap - nonlin - phase
        return I + dt * dI

    def compute_temporal_dynamics(self, tau: np.ndarray, I: np.ndarray, *, dt: float = 0.1) -> np.ndarray:
        grad0, grad1 = np.gradient(tau)
        rho2 = grad0**2 + grad1**2
        f = 1.0 / (2.0 * (1.0 + rho2**2))

        div = (
            (f[2:, 1:-1] * (tau[2:, 1:-1] - tau[1:-1, 1:-1]) - f[:-2, 1:-1] * (tau[1:-1, 1:-1] - tau[:-2, 1:-1]))
            + (f[1:-1, 2:] * (tau[1:-1, 2:] - tau[1:-1, 1:-1]) - f[1:-1, :-2] * (tau[1:-1, 1:-1] - tau[1:-1, :-2]))
        )
        div_full = np.zeros_like(tau)
        div_full[1:-1, 1:-1] = div

        phase = float(self.constants.lambda_3) * np.sin(tau - np.angle(I))
        return tau + dt * (div_full - phase)

    def evolution_step(self, *, dt: float = 0.1) -> Dict[str, float]:
        self.state.R_field[:] = self.compute_resonance(self.state.S_field, self.state.I_field)
        entropy = self.compute_symbolic_entropy(self.state.R_field)

        self.state.mass_field[:] = self.compute_symbolic_mass(self.state.S_field, self.state.I_field)

        B_field = np.ones_like(self.state.R_field) * 1e-4
        rho_field = self.state.mass_field + 1e-10
        self.state.Lambda0_field[:] = self.compute_lambda0_operator(B_field, rho_field)

        self.state.I_field[:] = self.compute_intention_dynamics(self.state.I_field, self.state.tau_field, dt=dt)
        self.state.tau_field[:] = self.compute_temporal_dynamics(self.state.tau_field, self.state.I_field, dt=dt)

        self.state.S_field[:] = self.state.S_field + dt * 0.1 * self.state.I_field

        return {
            'resonance_mean': float(np.mean(self.state.R_field)),
            'entropy_mean': float(np.mean(entropy)),
            'mass_mean': float(np.mean(self.state.mass_field)),
            'lambda0_mean': float(np.mean(np.abs(self.state.Lambda0_field))),
        }

    def step(self, *, dt: float = 0.1) -> Dict[str, float]:
        return self.evolution_step(dt=dt)

    def run(self, *, steps: int = 50, dt: float = 0.1) -> Dict[str, Any]:
        last: Dict[str, float] = {}
        for _ in range(int(steps)):
            last = self.step(dt=dt)
        return {'final': last}
