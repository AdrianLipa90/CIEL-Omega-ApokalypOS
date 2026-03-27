"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Dynamic ethical evaluation, static check, moral decay, and monitor glue.

Sources: ext4.EthicalEngine, ext4.EthicalCoreLite, ext4.ethical_decay,
         ext4.energy_to_time, ext4.EthicalMonitor
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Dynamic ethical engine
# ---------------------------------------------------------------------------

@dataclass
class EthicalEngine:
    """Dynamic ethical evaluation: (coherence × intention) / mass → tanh."""

    bound: float = 0.9
    history: list = field(default_factory=list)

    def evaluate(self, coherence: float, intention: float, mass: float) -> float:
        score = (coherence * intention) / (mass + 1e-12)
        value = float(np.tanh(score / self.bound))
        self.history.append(value)
        return value

    def mean_score(self) -> float:
        return float(np.mean(self.history)) if self.history else 0.0


# ---------------------------------------------------------------------------
# Static (lite) check
# ---------------------------------------------------------------------------

class EthicalCoreLite:
    """Minimal static guard — quick boolean coherence × resonance test."""

    ETHICAL_BOUND = 0.9
    HARMONIC_TOL = 0.05

    @staticmethod
    def check(coherence: float, resonance: float) -> bool:
        return (coherence * resonance) > (
            EthicalCoreLite.ETHICAL_BOUND - EthicalCoreLite.HARMONIC_TOL
        )


# ---------------------------------------------------------------------------
# Moral energy decay
# ---------------------------------------------------------------------------

def ethical_decay(E: float, tau: float = 0.05) -> float:
    """Relaxation of moral tension — exponential decay model."""
    return float(np.exp(-E * tau))


def energy_to_time(E: float, h: float = 6.626_070_15e-34) -> float:
    """Convert energy to time in the ethical dimension."""
    return h / (E + 1e-12)


# ---------------------------------------------------------------------------
# Monitor (glue: engine + lite guard + color)
# ---------------------------------------------------------------------------

@dataclass
class EthicalMonitor:
    """Combines dynamic evaluation with static check and colour feedback."""

    engine: EthicalEngine = field(default_factory=EthicalEngine)
    lite: EthicalCoreLite = field(default_factory=EthicalCoreLite)

    def evaluate_and_color(
        self, coherence: float, intention: float, mass: float
    ) -> Tuple[float, Tuple[float, float, float]]:
        from ciel_omega.visualization.color_map import ColorMap  # lazy to avoid circular

        value = self.engine.evaluate(coherence, intention, mass)
        ok = self.lite.check(coherence, value)
        color = ColorMap.map_value(value if ok else value * 0.5)
        return value, color


__all__ = [
    "EthicalEngine",
    "EthicalCoreLite",
    "ethical_decay",
    "energy_to_time",
    "EthicalMonitor",
]
