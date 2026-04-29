"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Ω Runtime — main loop: drift → CSF → RCDE → memory → backend → metrics.

Source: ext20.OmegaRuntime
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

import numpy as np

from calibration.rcde import RCDECalibratorPro
from cognition.introspection import Introspection
from core.math_utils import coherence_metric, field_norm
from core.physics.csf_simulator import CSF2Kernel, CSF2State
from memory.synchronizer import MemorySynchronizer
from runtime.backend_adapter import BackendAdapter
from runtime.omega.drift_core import OmegaDriftCorePlus


@dataclass
class OmegaRuntime:
    """Main Ω loop orchestrator."""

    backend: BackendAdapter
    drift: OmegaDriftCorePlus
    rcde: RCDECalibratorPro
    csf: CSF2Kernel
    memory: MemorySynchronizer = field(default_factory=MemorySynchronizer)
    introspection: Introspection = field(default_factory=Introspection)

    def step(
        self, state: CSF2State, backend_steps: int = 3, backend_dt: float = 0.02
    ) -> Tuple[CSF2State, Dict[str, float]]:
        sigma_scalar = float(np.clip(np.mean(state.sigma), 0.0, 1.0))

        # 1) Ω-drift
        psi_d = self.drift.step(state.psi, sigma_scalar=sigma_scalar)
        # 2) CSF local dynamics
        s_loc = CSF2State(psi_d, state.sigma, state.lam, state.omega)
        s_loc = self.csf.step(s_loc)
        # 3) RCDE Σ update
        new_sigma_scalar = self.rcde.step(sigma_scalar, s_loc.psi)
        # 4) Memory + introspection
        ms = self.memory.update(s_loc.sigma, s_loc.psi)
        ego_state = self.introspection.state(s_loc.psi, s_loc.psi * np.exp(1j * 0.2))
        # 5) Backend evolve
        self.backend.set_fields(s_loc.psi, s_loc.sigma)
        for _ in range(backend_steps):
            self.backend.step(dt=backend_dt)
        psi_b, sigma_b = self.backend.get_fields()
        # 6) Assemble output
        s_out = CSF2State(
            psi_b / (field_norm(psi_b)),
            np.clip(sigma_b, 0, 2.0),
            s_loc.lam,
            s_loc.omega,
        )
        metrics = {
            "coherence": coherence_metric(s_out.psi),
            "sigma_mean": float(np.mean(s_out.sigma)),
            "sigma_rcde": new_sigma_scalar,
            "memory_mean": float(np.mean(ms)),
            "ego_rho": float(ego_state["rho"]),
        }
        return s_out, metrics


__all__ = ["OmegaRuntime"]
