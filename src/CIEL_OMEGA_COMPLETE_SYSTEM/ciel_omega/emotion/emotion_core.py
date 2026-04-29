"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Core emotional state vector with inertia-based updates.

Source: ext9.EmotionCore
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import numpy as np


@dataclass
class EmotionCore:
    """Compact emotion state: 6 components in [0,1] with soft normalisation."""

    state: Dict[str, float] = field(default_factory=lambda: {
        "joy": 0.40, "calm": 0.50, "awe": 0.25,
        "sadness": 0.20, "anger": 0.10, "stress": 0.15,
        "compassion": 0.0,
    })
    inertia: float = 0.85

    def _norm(self) -> None:
        v = np.array(list(self.state.values()), dtype=float)
        vmax = float(np.max(v)) + 1e-12
        v = v / vmax
        for k, val in zip(self.state.keys(), v):
            self.state[k] = float(np.clip(val, 0.0, 1.0))

    def update(self, affect: Dict[str, float]) -> Dict[str, float]:
        for k, v in affect.items():
            if k in self.state:
                self.state[k] = float(self.inertia * self.state[k] + (1 - self.inertia) * v)
        self._norm()
        return dict(self.state)

    def summary_scalar(self) -> float:
        """Mood scalar: (joy+calm+awe+compassion) − (sadness+anger+stress) → [0,1]."""
        pos = self.state.get("joy", 0) + self.state.get("calm", 0) + self.state.get("awe", 0) + self.state.get("compassion", 0)
        neg = self.state.get("sadness", 0) + self.state.get("anger", 0) + self.state.get("stress", 0)
        return float(np.clip(0.5 * (1.0 + np.tanh(0.8 * (pos - neg))), 0.0, 1.0))


__all__ = ["EmotionCore"]
