from __future__ import annotations

from dataclasses import dataclass, field
import sys
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np

from .batch18 import OmegaDriftCorePlus, RCDECalibratorPro
from .csf2 import CSF2Kernel, CSF2State, Introspection, MemorySynchronizer
from .field_ops import coherence_metric, field_norm, normalize_field
from .schumann import SchumannClock


class BackendAdapter:
    def __init__(self, backend: Optional[Any] = None, grid_size: int = 96) -> None:
        self.backend = backend
        self.grid_size = int(grid_size)

        self._fallback_kernel = CSF2Kernel(dt=0.02)
        self._fallback_state: Optional[Tuple[np.ndarray, np.ndarray]] = None

        if self.backend is None:
            x = np.linspace(-2.0, 2.0, int(grid_size))
            X, Y = np.meshgrid(x, x)
            psi = np.exp(-(X**2 + Y**2)) * np.exp(1j * (X + 0.2 * Y))
            psi = normalize_field(psi)
            sigma = np.exp(-(X**2 + Y**2) / 2.0)
            self._fallback_state = (psi.astype(np.complex128), sigma.astype(np.float64))

    def set_fields(self, psi: np.ndarray, sigma: np.ndarray) -> None:
        if self.backend is not None and hasattr(self.backend, 'set_fields'):
            self.backend.set_fields(psi, sigma)
        else:
            self._fallback_state = (psi.copy(), sigma.copy())

    def step(self, dt: float) -> None:
        if self.backend is not None and hasattr(self.backend, 'step'):
            self.backend.step(dt=dt)
            return

        if self._fallback_state is None:
            return
        psi, sigma = self._fallback_state
        s = CSF2State(psi, sigma, np.ones_like(psi) * 0.1, np.zeros_like(sigma))
        self._fallback_kernel.dt = float(dt)
        s2 = self._fallback_kernel.step(s)
        self._fallback_state = (s2.psi, s2.sigma)

    def get_fields(self) -> Tuple[np.ndarray, np.ndarray]:
        if self.backend is not None and hasattr(self.backend, 'get_fields'):
            return self.backend.get_fields()
        assert self._fallback_state is not None
        return self._fallback_state


@dataclass
class OmegaRuntime:
    backend: BackendAdapter
    drift: OmegaDriftCorePlus
    rcde: RCDECalibratorPro
    csf: CSF2Kernel
    memory: MemorySynchronizer = field(default_factory=MemorySynchronizer)
    introspection: Introspection = field(default_factory=Introspection)

    def step(self, state: CSF2State, *, backend_steps: int = 3, backend_dt: float = 0.02) -> Tuple[CSF2State, Dict[str, float]]:
        sigma_scalar = float(np.clip(float(np.mean(state.sigma)), 0.0, 1.0))
        psi_d = self.drift.step(state.psi, sigma_scalar=sigma_scalar)

        s_loc = CSF2State(psi_d, state.sigma, state.lam, state.omega)
        s_loc = self.csf.step(s_loc)

        self.rcde.step(s_loc.psi)

        ms = self.memory.update(s_loc.sigma, s_loc.psi)
        rho, _st = self.introspection.state(s_loc.psi, s_loc.psi * np.exp(1j * 0.2))

        self.backend.set_fields(s_loc.psi, s_loc.sigma)
        for _ in range(int(backend_steps)):
            self.backend.step(dt=float(backend_dt))
        psi_b, sigma_b = self.backend.get_fields()

        s_out = CSF2State(normalize_field(psi_b), np.clip(sigma_b, 0.0, 2.0), s_loc.lam, s_loc.omega)
        metrics = {
            'coherence': float(coherence_metric(s_out.psi)),
            'sigma_mean': float(np.mean(s_out.sigma)),
            'sigma_rcde': float(self.rcde.sigma),
            'memory_mean': float(np.mean(ms)),
            'ego_rho': float(rho),
        }
        return s_out, metrics


def make_seed(n: int = 96) -> CSF2State:
    x = np.linspace(-2.0, 2.0, int(n))
    X, Y = np.meshgrid(x, x)
    psi = np.exp(-(X**2 + Y**2)) * np.exp(1j * (X + 0.2 * Y))
    psi = normalize_field(psi)
    sigma = np.exp(-(X**2 + Y**2) / 2.0)
    lam = np.ones_like(psi) * 0.1
    omega = np.zeros_like(sigma)
    return CSF2State(psi.astype(np.complex128), sigma.astype(np.float64), lam.astype(np.complex128), omega.astype(np.float64))


def build_runtime(*, backend_obj: Optional[Any] = None, grid: int = 96) -> OmegaRuntime:
    backend = BackendAdapter(backend_obj, grid_size=int(grid))
    drift = OmegaDriftCorePlus(SchumannClock(), drift_gain=0.04, harmonic_sweep=(1, 3), jitter=0.003)
    rcde = RCDECalibratorPro(lam=0.22, dt=0.05, sigma=0.6)
    csf = CSF2Kernel(dt=0.05)
    return OmegaRuntime(backend=backend, drift=drift, rcde=rcde, csf=csf)


def run_demo(
    *,
    steps: int = 20,
    n: int = 96,
    backend_obj: Optional[Any] = None,
    backend_steps: int = 3,
    backend_dt: float = 0.02,
    every: int = 0,
    progress: bool = False,
    max_seconds: float = 0.0,
) -> Dict[str, float]:
    rt = build_runtime(backend_obj=backend_obj, grid=int(n))
    st = make_seed(int(n))
    last: Dict[str, float] = {}
    t0 = time.perf_counter()

    steps_i = int(steps)
    every_i = int(every)
    backend_steps_i = int(backend_steps)
    backend_dt_f = float(backend_dt)
    max_seconds_f = float(max_seconds)

    for i in range(1, steps_i + 1):
        if max_seconds_f > 0.0 and (time.perf_counter() - t0) > max_seconds_f:
            break
        st, last = rt.step(st, backend_steps=backend_steps_i, backend_dt=backend_dt_f)
        if progress and every_i > 0 and (i % every_i == 0 or i == steps_i):
            elapsed = time.perf_counter() - t0
            print(
                f"omega20 step={i}/{steps_i} coh={last.get('coherence', float('nan')):.6f} "
                f"sigma={last.get('sigma_mean', float('nan')):.4f} elapsed={elapsed:.2f}s",
                file=sys.stderr,
                flush=True,
            )

    return last
