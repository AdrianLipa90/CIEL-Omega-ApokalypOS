"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Ω boot ritual — phase/intention warm-up sequence.

Source: ext18.OmegaBootRitual
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

import numpy as np

from ciel_omega.core.math_utils import coherence_metric, field_norm, laplacian2
from ciel_omega.runtime.omega.drift_core import OmegaDriftCorePlus


@dataclass
class OmegaBootRitual:
    """Warm-up sequence: iterate Ω-drift + intent bias to reach coherent state."""

    drift: OmegaDriftCorePlus
    steps: int = 16
    intent_bias: float = 0.12
    log: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def run(self, psi0: np.ndarray, sigma0: float = 0.5) -> Dict[str, Any]:
        psi = psi0.copy()
        sigma = float(sigma0)
        for i in range(self.steps):
            psi *= np.exp(1j * self.intent_bias)
            psi = self.drift.step(psi, sigma_scalar=sigma)
            psi = psi + 1j * 0.01 * laplacian2(psi)
            psi /= field_norm(psi)
            sigma = float(np.clip(0.92 * sigma + 0.08 * field_norm(psi) ** 2, 0.0, 1.2))
            self.log.append({"step": i, "sigma": sigma, "coh": coherence_metric(psi)})
        return {
            "psi": psi,
            "sigma": sigma,
            "coherence": coherence_metric(psi),
            "boot_complete": True,
        }


__all__ = ["OmegaBootRitual"]
