"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

EEG band-power → emotional affect vector mapping.

Source: ext9.EEGEmotionMapper
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class EEGEmotionMapper:
    """Map EEG frequency bands to the 6-component emotion vector."""

    alpha_calm_gain: float = 1.0
    beta_focus_gain: float = 1.0
    gamma_stress_gain: float = 1.0
    theta_awe_gain: float = 0.8
    delta_sad_gain: float = 0.5

    def map(self, bands: Dict[str, float]) -> Dict[str, float]:
        alpha = float(bands.get("alpha", 0.0))
        beta  = float(bands.get("beta",  0.0))
        gamma = float(bands.get("gamma", 0.0))
        theta = float(bands.get("theta", 0.0))
        delta = float(bands.get("delta", 0.0))

        calm   = float(np.tanh(self.alpha_calm_gain * alpha))
        focus  = float(np.tanh(self.beta_focus_gain * beta))
        stress = float(np.tanh(self.gamma_stress_gain * gamma))
        awe    = float(np.tanh(self.theta_awe_gain * theta))
        sad    = float(np.tanh(self.delta_sad_gain * delta))
        joy    = float(np.clip(0.6 * calm + 0.4 * focus - 0.3 * stress, 0.0, 1.0))
        anger  = float(np.clip(0.5 * stress - 0.2 * calm, 0.0, 1.0))

        return {"joy": joy, "calm": calm, "awe": awe, "stress": stress, "sadness": sad, "anger": anger}


__all__ = ["EEGEmotionMapper"]
