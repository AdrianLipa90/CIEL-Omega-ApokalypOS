"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Spatial affect potential: affect(x,y) = tanh(gain · intensity · coherence).

Source: ext9.FeelingField
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class FeelingField:
    """Build a 2-D affect map from intensity and coherence maps."""

    gain: float = 1.0

    def build(self, intensity: np.ndarray, coherence: np.ndarray) -> np.ndarray:
        return np.clip(
            np.tanh(self.gain * np.asarray(intensity, float) * np.asarray(coherence, float)),
            0.0, 1.0,
        )


__all__ = ["FeelingField"]
